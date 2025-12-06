"""
Main prediction pipeline
Entry point: Reads /code/private_test.json, outputs submission.csv
"""
import json
import csv
import os
import sys
from typing import List, Dict

# Import modules
from modules.question_classifier import classifier
from modules.categories import QuestionCategory
from modules.llm.api_client import llm_client
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

        # TODO: Load vector DBs if they exist
        # self.vector_dbs = self._load_vector_dbs()

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
                # TODO: Use RAG retrieval
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
        return "A"  # Fallback

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
        """Handle math/logic questions with improved strategy"""
        # Build math prompt with few-shot examples
        prompt = self._build_math_prompt(question, choices)

        # Use Large model for complex math, Small for simple
        # Heuristic: if question is short and has few numbers, use Small (faster)
        question_len = len(question)
        num_count = len([c for c in question if c.isdigit()])

        # Use Small model if simple (save API quota and faster)
        if question_len < 200 and num_count < 10:
            model = "small"
            temp = 0.2
        else:
            model = "large"
            temp = 0.1

        response = self.llm.generate(prompt, model=model, temperature=temp)

        # Extract answer with improved parsing
        answer = self._extract_answer(response, choices)

        # Validate answer is in valid range
        valid_letters = [chr(65 + i) for i in range(len(choices))]
        if answer not in valid_letters:
            # Try harder to find valid answer in response
            import re
            # Look for last occurrence of valid letter
            for letter in reversed(valid_letters):
                if letter in response.upper():
                    answer = letter
                    break

            # Still invalid? Try response ending
            end_part = response[-200:].upper()
            for letter in valid_letters:
                if letter in end_part:
                    answer = letter
                    break

        return answer if answer in valid_letters else valid_letters[0]

    def _handle_domain_question(
        self,
        question: str,
        choices: List[str],
        category: QuestionCategory
    ) -> str:
        """Handle domain-specific questions (with simple knowledge augmentation)"""

        # Build base prompt
        base_prompt = self._build_domain_prompt(question, choices, category)

        # Augment with simple facts (lightweight RAG alternative)
        augmented_prompt = augment_prompt_with_facts(question, base_prompt)

        # Use Small model (faster, cheaper)
        response = self.llm.generate(augmented_prompt, model="small", temperature=0.3)

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
        """Build prompt for math questions with few-shot examples"""
        choices_text = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])

        # Determine valid answer range
        max_letter = chr(65 + len(choices) - 1)

        # Few-shot examples to guide the model
        examples = """Ví dụ 1:
Câu hỏi: Tính diện tích hình chữ nhật có chiều dài 5m và chiều rộng 3m?
Các đáp án: A. 8m² B. 15m² C. 30m² D. 10m²
Giải: Diện tích = dài × rộng = 5 × 3 = 15m²
Đáp án: B

Ví dụ 2:
Câu hỏi: Điện trở tương đương khi hai điện trở R1=6Ω và R2=3Ω mắc song song?
Các đáp án: A. 9Ω B. 3Ω C. 2Ω D. 4.5Ω
Giải: R_tương đương = (R1 × R2)/(R1 + R2) = (6 × 3)/(6 + 3) = 18/9 = 2Ω
Đáp án: C

---"""

        prompt = f"""{examples}

Bây giờ hãy giải bài toán sau theo cách tương tự:

Câu hỏi: {question}

Các đáp án:
{choices_text}

Yêu cầu:
1. Đọc kỹ đề, xác định công thức cần dùng
2. Thay số và tính toán từng bước
3. So sánh kết quả với các đáp án
4. Chọn đáp án khớp với kết quả tính được

Lưu ý: CHỈ chọn từ {chr(65)} đến {max_letter}. Không được chọn ngoài range này.

Hãy giải chi tiết rồi kết luận đáp án cuối cùng.
Đáp án cuối cùng (CHỈ ghi MỘT chữ cái):"""
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

        # Method 3: Find any valid letter in entire response (last resort)
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
            return 'A'


def main():
    """Main entry point"""
    # Paths
    input_path = "/code/data/private_test.json"  # Docker will mount this
    output_path = "/code/output/submission.csv"

    # For local testing
    if not os.path.exists(input_path):
        input_path = "data/val.json"  # Use full validation set
        output_path = "submission.csv"

    print(f"Reading from: {input_path}")
    print(f"Writing to: {output_path}")

    # Load questions
    with open(input_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions")

    # Initialize pipeline
    pipeline = SimplePipeline()

    # Write CSV header first
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['qid', 'answer'])
        writer.writeheader()

    # Predict and write incrementally
    results = []
    for i, q in enumerate(questions):
        qid = q['qid']
        question = q['question']
        choices = q['choices']

        print(f"\n[{i+1}/{len(questions)}] Processing {qid}...")

        try:
            answer = pipeline.predict_single(question, choices, qid)
        except Exception as e:
            print(f"ERROR: {e}")
            answer = 'A'  # Fallback

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
        if (i + 1) % 10 == 0:
            print(f"✓ Saved progress: {i+1}/{len(questions)} questions")

    print(f"\n✓ Done! Output written to {output_path}")
    print(f"Total questions processed: {len(results)}")


if __name__ == "__main__":
    main()
