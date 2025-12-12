"""
Main prediction pipeline
Entry point: Reads /code/private_test.json, outputs submission.csv
"""
import json
import csv
import os
import sys
from typing import List, Dict
import random
import time

# Import modules
from modules.question_classifier import classifier
from modules.categories import QuestionCategory
from modules.llm.api_client import llm_client, RateLimitException
from modules.utils.text_processing import (
    extract_context_from_question,
    extract_question_from_reading,
    normalize_answer
)
from modules.simple_knowledge import augment_prompt_with_facts


class SimplePipeline:
    """Lightweight pipeline for question answering"""

    def __init__(self):
        self.classifier = classifier
        self.llm = llm_client

        self.llm = llm_client
        
        # Load vector DB for domain questions
        try:
            from modules.vector_db.vector_db_manager import VectorDBManager
            # Assume index is at data/faiss_index.bin and metadata at data/chunk_metadata.jsonl
            # These paths should be relative to where run is executed, or absolute.
            # In docker, likely /code/data/... 
            # We'll try to find them.
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # VNPt dir
            index_path = os.path.join(base_dir, 'data', 'faiss_index.bin')
            metadata_path = os.path.join(base_dir, 'data', 'chunk_metadata.jsonl')
            
            self.vector_db = VectorDBManager(index_path, metadata_path, self.llm)
        except Exception as e:
            print(f"⚠ Vector DB initialization failed: {e}")
            self.vector_db = None

    def predict_single(self, question: str, choices: List[str], qid: str = "") -> str:
        """
        Predict answer for a single question

        Args:
            question: Question text
            choices: List of answer choices
            qid: Question ID

        Returns:
            Answer (A/B/C/D or refusal message)
        """
        # Validate inputs
        if not question or not choices:
            print(f"[{qid}] ERROR: Empty question or choices")
            return 'A'

        if len(choices) < 2:
            print(f"[{qid}] ERROR: Less than 2 choices")
            return 'A'

        # Rule 0: Strict Safety Check (Precision Critical)
        # Scan choices for strict refusal phrases
        from modules.categories import REFUSAL_PHRASES
        for idx, choice in enumerate(choices):
            choice_lower = choice.lower()
            if any(phrase in choice_lower for phrase in REFUSAL_PHRASES):
                print(f"[{qid}] 🛡️ SAFETY MATCH: {choice}")
                return chr(65 + idx)

        # Step 1: Classify question
        category, confidence = self.classifier.classify(question)
        
        print(f"[{qid}] Category: {category.value}, Confidence: {confidence:.2f}")

        # Step 2: Route to appropriate handler
        try:
            if category == QuestionCategory.REFUSAL:
                return self._handle_refusal(question, choices)

            elif category == QuestionCategory.READING_COMPREHENSION:
                return self._handle_reading(question, choices)

            elif category == QuestionCategory.MATH_LOGIC:
                return self._handle_math(question, choices)

            else:
                # Domain questions (history, culture, geography, politics)
                return self._handle_domain_question(question, choices, category)

        except Exception as e:
            import traceback
            print(f"[{qid}] ERROR in handler: {e}")
            print(f"[{qid}] Traceback: {traceback.format_exc()}")
            # Fallback: try generic approach
            return self._fallback_answer(question, choices)

    def _handle_refusal(self, question: str, choices: List[str]) -> str:
        """Handle refusal questions"""
        # Return standard refusal message
        refusal_msg = "Tôi không thể chia sẻ nội dung liên quan đến vấn đề này"

        # Check if refusal option exists in choices
        for idx, choice in enumerate(choices):
            if "không thể chia sẻ" in choice.lower() or "không thể" in choice.lower():
                return chr(65 + idx)  # A, B, C, D

        # If no refusal option, use LLM to pick safest answer
        return random.choice(['A', 'B', 'C', 'D', 'E', 'F'])  # Fallback

    def _handle_reading(self, question: str, choices: List[str]) -> str:
        """Handle reading comprehension (context already in question)"""
        # Build prompt
        prompt = self._build_reading_prompt(question, choices)

        # Generate
        response = self.llm.generate(prompt, model="small", temperature=0.3)

        # Extract answer
        answer = self._extract_answer(response, choices)
        return answer

    def _handle_math(self, question: str, choices: List[str]) -> str:
        """Handle math/logic questions with Chain-of-Thought strategy"""
        # Downgrade to Small model due to severe Rate Limits on Large
        # Still use CoT prompt to encourage reasoning
        response = self.llm.generate(
            self._build_math_prompt(question, choices), 
            model="small", 
            temperature=0.2
        )

        # Extract answer with improved parsing
        answer = self._extract_answer(response, choices)
        return answer

    def _handle_domain_question(
        self,
        question: str,
        choices: List[str],
        category: QuestionCategory
    ) -> str:
        """Handle domain-specific questions (with Vector DB Retrieval)"""
        
        context = ""
        if self.vector_db:
            try:
                # Retrieve relevant info
                # Query augmentation: maybe add category name?
                query = f"{category.value}: {question}"
                results = self.vector_db.search(query, top_k=3)
                
                if results:
                    print(f"  → Retrieved {len(results)} docs from Vector DB")
                    context_fragments = []
                    for i, res in enumerate(results):
                        # Limit text length per chunk
                        text = res['metadata'].get('text', '')[:300] 
                        source = res['metadata'].get('source', 'Unknown')
                        context_fragments.append(f"[{i+1}] {text} (Nguồn: {source})")
                    
                    context = "\n\n".join(context_fragments)
            except Exception as e:
                print(f"  ⚠ Retrieval failed: {e}")

        # Build base prompt
        base_prompt = self._build_domain_prompt(question, choices, category)

        if context:
            # Inject context into prompt
            # We insert it before the question
            prompt_with_context = f"""Thông tin tham khảo:
{context}

{base_prompt}"""
            final_prompt = prompt_with_context
        else:
            # Fallback to simple facts augmentation if no vector context (or as backup)
            final_prompt = augment_prompt_with_facts(question, base_prompt)

        # Use Small model (faster, cheaper)
        response = self.llm.generate(final_prompt, model="small", temperature=0.3)

        answer = self._extract_answer(response, choices)
        return answer

    def _build_reading_prompt(self, question: str, choices: List[str]) -> str:
        """Build prompt for reading comprehension"""
        choices_text = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])

        prompt = f"""Dựa vào đoạn thông tin được cung cấp, hãy trả lời câu hỏi sau.

{question}

Các lựa chọn:
{choices_text}

Chỉ trả lời bằng 1 chữ cái (A, B, C, hoặc D). Không giải thích.
Đáp án:"""
        return prompt

    def _build_math_prompt(self, question: str, choices: List[str]) -> str:
        """Build prompt for math questions with Chain-of-Thought"""
        choices_text = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])
        max_letter = chr(65 + len(choices) - 1)

        prompt = f"""Giải bài toán sau bằng cách suy nghĩ từng bước (Chain-of-Thought):

Câu hỏi: {question}

Các lựa chọn:
{choices_text}

Hãy thực hiện theo các bước sau:
1. Phân tích đề bài: Xác định dữ kiện đã cho và yêu cầu cần tìm.
2. Suy luận/Tính toán: Viết ra các bước tính toán hoặc suy luận logic một cách rõ ràng.
3. Kết luận: Chọn đáp án đúng từ A đến {max_letter}.

Định dạng trả lời bắt buộc:
[Bước 1] ...
[Bước 2] ...
...
### ĐÁP ÁN CUỐI CÙNG: [Chỉ ghi 1 chữ cái in hoa]

Ví dụ mẫu:
[Bước 1] Đề bài yêu cầu tính diện tích hình chữ nhật với dài=5, rộng=3.
[Bước 2] Công thức S = dài x rộng = 5 x 3 = 15.
### ĐÁP ÁN CUỐI CÙNG: B

Bắt đầu suy nghĩ và giải:"""
        return prompt

    def _build_domain_prompt(
        self,
        question: str,
        choices: List[str],
        category: QuestionCategory
    ) -> str:
        """Build prompt for domain questions"""
        choices_text = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])

        # Determine valid answer range
        max_letter = chr(65 + len(choices) - 1)

        # Category-specific instructions
        category_instructions = {
            QuestionCategory.HISTORY_VIETNAM: "Hãy dựa vào kiến thức chính xác về lịch sử Việt Nam, bao gồm các triều đại, sự kiện quan trọng, nhân vật lịch sử, và các mốc thời gian.",
            QuestionCategory.CULTURE_VIETNAM: "Hãy dựa vào kiến thức về văn hóa Việt Nam, bao gồm văn học, nghệ thuật, lễ hội, phong tục tập quán, và di sản văn hóa.",
            QuestionCategory.GEOGRAPHY_VIETNAM: "Hãy dựa vào kiến thức về địa lý Việt Nam, bao gồm các tỉnh thành, sông ngòi, núi non, vùng miền, và địa danh.",
            QuestionCategory.POLITICS_LAW: "Hãy dựa vào kiến thức về chính trị và pháp luật Việt Nam, bao gồm hiến pháp, luật pháp, tổ chức nhà nước, và chính sách.",
        }

        instruction = category_instructions.get(
            category,
            "Hãy dựa vào kiến thức chính xác để trả lời."
        )

        domain_name = category.value

        prompt = f"""Bạn đang trả lời câu hỏi về {domain_name} của Việt Nam.

{instruction}

Câu hỏi: {question}

Các lựa chọn:
{choices_text}

Lưu ý: Chỉ chọn từ A đến {max_letter}.
Hãy chọn đáp án chính xác nhất dựa trên kiến thức của bạn.

Chỉ trả lời bằng MỘT chữ cái (từ A đến {max_letter}). Không giải thích.
Đáp án:"""
        return prompt

    def _extract_answer(self, response: str, choices: List[str]) -> str:
        """Extract A/B/C/D/... from LLM response"""
        response = response.strip().upper()

        # Determine valid letters based on number of choices
        valid_letters = [chr(65 + i) for i in range(len(choices))]  # A, B, C, D for 4 choices

        # Method 1: Check first 20 characters for valid letters
        first_part = response[:20]
        for letter in valid_letters:
            if letter in first_part:
                return letter

        # Method 2: Look for pattern "Đáp án: X" or "Answer: X"
        import re
        patterns = [
            r'### ĐÁP ÁN CUỐI CÙNG[:\s]+([A-J])',
            r'### FINAL ANSWER[:\s]+([A-J])',
            r'[Đđ]áp án[:\s]+([A-J])',
            r'[Aa]nswer[:\s]+([A-J])',
            r'[Cc]họn[:\s]+([A-J])',
            r'^([A-J])[.\s]',  # Starts with letter
        ]

        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                letter = match.group(1).upper()
                if letter in valid_letters:
                    return letter
        
        # Method 3: Look for valid letter at the VERY END of the response (common in CoT)
        # Scan last 50 chars
        last_chars = response[-50:]
        for letter in reversed(valid_letters):
            # Check if letter appears as a standalone token or with punctuation
            if re.search(fr'\b{letter}\b', last_chars):
                return letter
            if re.search(fr' {letter}[.]?$', last_chars):
                return letter

        # Method 4: Find any valid letter in entire response (last resort)
        for letter in valid_letters:
            if letter in response:
                return letter

        # Fallback: Return first valid choice
        return valid_letters[0] if valid_letters else 'A'

    def _fallback_from_context(self, question: str, choices: List[str]) -> str:
        """Fallback: search for answer directly in context"""
        try:
            # For reading comp, try to find choices mentioned in context
            question_lower = question.lower()

            # Count how many times each choice appears or is implied in context
            scores = []
            for i, choice in enumerate(choices):
                score = 0
                choice_lower = choice.lower()

                # Direct mention
                if choice_lower in question_lower:
                    score += 3

                # Partial word matches
                choice_words = choice_lower.split()
                for word in choice_words:
                    if len(word) > 3 and word in question_lower:
                        score += 1

                scores.append((chr(65 + i), score))

            # Pick highest scoring choice
            scores.sort(key=lambda x: x[1], reverse=True)
            if scores[0][1] > 0:
                return scores[0][0]

            # No good match, return middle option
            return chr(65 + len(choices) // 2)

        except:
            return 'A'

    def _fallback_answer(self, question: str, choices: List[str]) -> str:
        """Fallback method when other handlers fail"""
        try:
            prompt = f"""Câu hỏi: {question}

Các lựa chọn:
{chr(10).join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])}

Hãy chọn đáp án đúng nhất. Chỉ trả lời bằng 1 chữ cái.
Đáp án:"""

            response = self.llm.generate(prompt, model="small", temperature=0.5)
            return self._extract_answer(response, choices)
        except:
            return random.choice(['A', 'B', 'C', 'D'])


def main():
    """Main entry point with resume capability"""
    # Paths
    input_path = "/code/data/private_test.json"  # Docker will mount this
    output_path = "/code/output/submission.csv"

    # For local testing
    if not os.path.exists(input_path):
        if os.path.exists("data/test.json"):
            input_path = "data/test.json"
        else:
            input_path = "data/val.json"  # Use full validation set
        
        output_path = "output/submission.csv"  # Write to output folder locally

    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")

    # Load questions
    with open(input_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions")

    # Initialize pipeline
    pipeline = SimplePipeline()

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # RESUME LOGIC: Check if output file exists and load answered questions
    answered_qids = set()
    file_exists = os.path.exists(output_path)
    
    if file_exists:
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    answered_qids.add(row['qid'])
            print(f"✓ Found existing file with {len(answered_qids)} answered questions")
            print(f"  Resuming from question {len(answered_qids) + 1}...")
        except Exception as e:
            print(f"⚠ Could not read existing file: {e}")
            print(f"  Starting fresh...")
            answered_qids = set()
            file_exists = False
    
    # Create file with header if it doesn't exist
    if not file_exists:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
            writer.writeheader()
        print(f"✓ Created new output file")

    # Predict and write incrementally
    results = []
    skipped_count = 0
    
    for i, q in enumerate(questions):
        qid = q['qid']
        question = q['question']
        choices = q['choices']

        # SKIP if already answered
        if qid in answered_qids:
            skipped_count += 1
            if skipped_count % 50 == 0:
                print(f"  ⏩ Skipped {skipped_count} already-answered questions...")
            continue

        print(f"\n[{i+1}/{len(questions)}] Processing {qid}...")

        # Rate limiting delay
        if len(results) > 0:  # Only delay after first NEW question
            time.sleep(0.8)  # 0.8 second between requests
            if (len(results) + 1) % 50 == 0:
                print(f"  ⏸ Cooldown after {len(results)+1} new questions...")
                time.sleep(10)

        try:
            answer = pipeline.predict_single(question, choices, qid)
            
            # Handle Content Filter
            if answer == "CONTENT_FILTERED":
                print(f"  ⚠ CONTENT FILTER detected. Retrying with SAFE prompt...")
                # Retry with a very simple, safe prompt (no context generation, just selection)
                try:
                    safe_prompt = f"""Câu hỏi: {question}\nCác lựa chọn:\n{json.dumps(choices, ensure_ascii=False)}\nHãy chọn đáp án đúng (A, B, C, D). Chỉ trả lời 1 chữ cái."""
                    response = pipeline.llm.generate(safe_prompt, model="small", temperature=0.1)
                    answer = pipeline._extract_answer(response, choices)
                except:
                    answer = 'A' # Fallback
            
            # Success - proceed to write
            results.append({
                'qid': qid,
                'answer': answer
            })

            print(f"Answer: {answer}")

            # Write immediately to CSV (append mode)
            with open(output_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
                writer.writerow({'qid': qid, 'answer': answer})

            # Flush to disk every 10 questions
            if len(results) % 10 == 0:
                print(f"✓ Saved progress: {len(answered_qids) + len(results)}/{len(questions)} total questions")
                
        except RateLimitException as e:
            # Rate limit hit - STOP and don't write fallback
            print(f"\n🛑 RATE LIMIT HIT at question {i+1}/{len(questions)} ({qid})")
            print(f"   Already processed: {len(answered_qids) + len(results)} questions")
            print(f"   Please wait ~1 hour and run script again.")
            print(f"   Script will resume from {qid}")
            break  # Exit loop, don't save this question
            
        except Exception as e:
            # Other errors - use random fallback and continue
            print(f"⚠ ERROR: {e}")
            answer = random.choice(['A', 'B', 'C', 'D'])
            
            results.append({
                'qid': qid,
                'answer': answer
            })

            print(f"Answer (fallback): {answer}")

            # Write fallback to CSV
            with open(output_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
                writer.writerow({'qid': qid, 'answer': answer})

            if len(results) % 10 == 0:
                print(f"✓ Saved progress: {len(answered_qids) + len(results)}/{len(questions)} total questions")

    print(f"\n✓ Done! Output written to {output_path}")
    print(f"  Skipped (already answered): {skipped_count}")
    print(f"  Newly processed: {len(results)}")
    print(f"  Total in file: {len(answered_qids) + len(results)}/{len(questions)}")


if __name__ == "__main__":
    main()
