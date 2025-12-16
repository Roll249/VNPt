import re
import math
import sys
import io
import traceback
from typing import List, Optional

try:
    from modules.llm.api_client import VNPTClient
except ImportError:
    # Fallback
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from modules.llm.api_client import VNPTClient

class MathSolver:
    """
    Program-Aided Language (PAL) Solver for Math questions.
    Generates and executes Python code to solve arithmetic/logic problems.
    """
    
    def __init__(self, llm_client: VNPTClient):
        self.llm = llm_client
        
    def solve(self, question: str, choices: List[str]) -> str:
        """
        Solve math question by generating and running code.
        Returns: Answer choice (A, B, C, or D) or None if failed.
        """
        print(f"    Running Code Solver...")

        # 1. Generate Code
        code = self._generate_code(question, choices)
        if not code:
            print("    Failed to generate code.")
            return None

        print(f"    Generated Code:\n{code}")

        # 2. Execute Code
        result = self._execute_code(code)
        if result is None:
            print("    Execution failed or empty output.")
            return None

        print(f"    Execution Result: {result}")

        # 3. Match Result to Choices
        best_choice = self._match_choice(result, choices)

        if best_choice:
             print(f"    Code Solver Conclusion: {best_choice}")
             return best_choice
        else:
             print("    Could not match result to choices.")
             return None

    def solve_with_context(self, question: str, choices: List[str], context: str) -> str:
        """
        Solve math/STEM question with context from retrieval.
        Context provides formulas, constants, and domain knowledge.

        NEW METHOD for Target 90%!

        Args:
            question: Question text
            choices: List of answer choices
            context: Retrieved STEM knowledge (formulas, concepts, etc.)

        Returns:
            Answer choice (A, B, C, or D) or None if failed.
        """
        print(f"    Running Code Solver with STEM context...")

        # 1. Extract formulas/constants from context
        formulas = self._extract_formulas_from_context(context)

        # 2. Generate Code with context
        code = self._generate_code_with_context(question, choices, formulas)
        if not code:
            print("    Failed to generate code with context.")
            return None

        print(f"    Generated Code:\n{code}")

        # 3. Execute Code
        result = self._execute_code(code)
        if result is None:
            print("    Execution failed or empty output.")
            return None

        print(f"    Execution Result: {result}")

        # 4. Match Result to Choices
        best_choice = self._match_choice(result, choices)

        if best_choice:
             print(f"    Code Solver with Context Conclusion: {best_choice}")
             return best_choice
        else:
             print("    Could not match result to choices.")
             return None

    def _extract_formulas_from_context(self, context: str) -> str:
        """Extract formulas and constants from STEM context"""
        if not context:
            return ""

        # Simple extraction: Look for common formula patterns
        formulas = []

        # Extract lines with = (equations)
        lines = context.split('\n')
        for line in lines[:10]:  # First 10 lines
            if '=' in line and len(line) < 100:  # Likely a formula
                formulas.append(line.strip())

        # Add common STEM constants
        constants_hints = """
# Common constants:
# g = 9.8  # Gravity (m/s²)
# c = 3e8  # Speed of light (m/s)
# R = 8.314  # Gas constant
# pi = 3.14159
"""

        if formulas:
            return "# Relevant formulas from context:\n" + "\n".join(f"# {f}" for f in formulas[:5]) + "\n" + constants_hints
        else:
            return constants_hints

    def _generate_code_with_context(self, question: str, choices: List[str], formulas: str) -> Optional[str]:
        """Generate code with STEM context/formulas"""
        choices_text = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])

        prompt = f"""Bạn là một lập trình viên Python giỏi. Hãy viết mã Python để giải bài toán STEM sau.

{formulas}

Câu hỏi: {question}

Các lựa chọn:
{choices_text}

Yêu cầu:
1. Viết code Python đơn giản, rõ ràng.
2. Sử dụng các công thức/constants phù hợp (nếu có trong context).
3. Đặt các biến cần thiết (ví dụ: v = 50, t = 2).
4. Thực hiện tính toán chính xác.
5. In ra kết quả cuối cùng sử dụng print().
6. CHỈ dùng thư viện chuẩn Python (standard library). Nếu cần toán học, chỉ dùng `math`.
7. KHÔNG dùng các thư viện ngoài như sympy/numpy/pandas.
8. CHỈ dùng tên biến ASCII (a-z, A-Z, 0-9, dấu gạch dưới). KHÔNG dùng ký tự chỉ số dưới/superscript như ₀ ₁ ² ³.
9. KHÔNG dùng biến ký hiệu dạng chuỗi (ví dụ s = 's') để làm đại số ký hiệu; bài này cần tính ra giá trị số.
10. KHÔNG dùng input(). KHÔNG cần comment giải thích dài dòng.
11. Chỉ viết code trong cặp dấu ```python và ```.

Code:"""

        # Use Large Model with Low Temp for coding
        response = self.llm.generate(prompt, model="large", temperature=0.1)

        # Extract code block
        match = re.search(r"```python(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: maybe just code without blocks?
        if "def " in response or "print(" in response:
            return response.strip()

        return None

    def _generate_code(self, question: str, choices: List[str]) -> Optional[str]:
        """Ask LLM to write Python code"""
        choices_text = "\n".join([f"{chr(65+i)}. {c}" for i, c in enumerate(choices)])
        
        prompt = f"""Bạn là một lập trình viên Python giỏi. Hãy viết mã Python để giải bài toán sau.

Câu hỏi: {question}

Các lựa chọn:
{choices_text}

Yêu cầu:
1. Viết code Python đơn giản, rõ ràng.
2. Đặt các biến cần thiết (ví dụ: v = 50, t = 2).
3. Thực hiện tính toán chính xác.
4. In ra kết quả cuối cùng sử dụng print().
5. CHỈ dùng thư viện chuẩn Python (standard library). Nếu cần toán học, chỉ dùng `math`.
6. KHÔNG dùng các thư viện ngoài như sympy/numpy/pandas.
7. CHỈ dùng tên biến ASCII (a-z, A-Z, 0-9, dấu gạch dưới). KHÔNG dùng ký tự chỉ số dưới/superscript như ₀ ₁ ² ³.
8. KHÔNG dùng biến ký hiệu dạng chuỗi (ví dụ s = 's') để làm đại số ký hiệu; bài này cần tính ra giá trị số.
9. KHÔNG dùng input(). KHÔNG cần comment giải thích dài dòng.
10. Chỉ viết code trong cặp dấu ```python và ```.

Code:"""
        
        # Use Large Model with Low Temp for coding
        response = self.llm.generate(prompt, model="large", temperature=0.1)
        
        # Extract code block
        match = re.search(r"```python(.*?)```", response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback: maybe just code without blocks?
        if "def " in response or "print(" in response:
            return response.strip()
            
        return None

    def _execute_code(self, code: str) -> Optional[str]:
        """Execute Python code and capture stdout"""
        # Normalize unicode subscripts (e.g., ω₀) that break Python parsing
        sub_map = str.maketrans({
            "₀": "0",
            "₁": "1",
            "₂": "2",
            "₃": "3",
            "₄": "4",
            "₅": "5",
            "₆": "6",
            "₇": "7",
            "₈": "8",
            "₉": "9",
        })
        code = (code or "").translate(sub_map)

        # Safety sandbox (basic)
        # Block dangerous imports
        banned = [
            "import os",
            "import sys",
            "subprocess",
            "import sympy",
            "from sympy",
            "import numpy",
            "from numpy",
            "import pandas",
            "from pandas",
        ]
        if any(b in code for b in banned):
            print("    Code contains potentially unsafe imports.")
            return None
            
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        
        try:
            # Add safe math imports
            exec_globals = {"math": math}
            exec(code, exec_globals)
            result = redirected_output.getvalue().strip()
            return result
        except Exception:
            traceback.print_exc(file=sys.stderr) # Print to real stderr for debug
            return None
        finally:
            sys.stdout = old_stdout

    def _parse_vietnamese_number(self, text: str) -> Optional[float]:
        """Parse Vietnamese number formats (NEW for Target 90%)

        Handles:
        - "1 triệu" → 1,000,000
        - "1 tỷ" → 1,000,000,000
        - "1.000.000" → 1,000,000 (European format)
        - "1,5 triệu" → 1,500,000
        """
        if not text:
            return None

        text = text.lower().strip()

        # Vietnamese multipliers
        multipliers = {
            "tỷ": 1_000_000_000,
            "ty": 1_000_000_000,
            "triệu": 1_000_000,
            "trieu": 1_000_000,
            "million": 1_000_000,
            "nghìn": 1_000,
            "nghin": 1_000,
            "vạn": 10_000,
            "van": 10_000,
        }

        # Try to match number + multiplier pattern
        for word, multiplier in multipliers.items():
            # Pattern: "123 triệu" or "123.5 triệu"
            pattern = rf"(\d+(?:[.,]\d+)?)\s*{word}"
            match = re.search(pattern, text)
            if match:
                num_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    base_num = float(num_str)
                    return base_num * multiplier
                except:
                    continue

        # Try European format: "1.000.000" (dots as thousands separator)
        # If has multiple dots and no comma, treat dots as thousands separator
        if text.count('.') >= 2 and ',' not in text:
            clean = text.replace('.', '')
            try:
                return float(clean)
            except:
                pass

        # Try standard number extraction
        # Remove thousand separators first
        clean_text = text.replace('.', '').replace(',', '.')

        # Extract number
        match = re.search(r"(\d+(?:\.\d+)?)", clean_text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass

        return None

    def _match_choice(self, result: str, choices: List[str]) -> Optional[str]:
        """Find which choice matches the result number (ENHANCED for Target 90%)"""
        try:
            def _to_float(s: str) -> float:
                s = (s or "").strip()
                # handle comma decimals
                if "," in s and "." not in s:
                    s = s.replace(",", ".")
                return float(s)

            def _extract_result_value(text: str) -> Optional[float]:
                if not text:
                    return None
                tl = text.strip().lower()

                # fraction like 20/3 in output
                m = re.search(r"([-+]?\d+(?:[\.,]\d+)?)\s*/\s*(\d+(?:[\.,]\d+)?)", tl)
                if m:
                    a = _to_float(m.group(1))
                    b = _to_float(m.group(2))
                    if b != 0:
                        return a / b

                # scientific notation or decimal/integer: take the last one
                nums = re.findall(r"[-+]?\d+(?:[\.,]\d+)?(?:e[-+]?\d+)?", tl)
                if not nums:
                    return None
                return _to_float(nums[-1])

            def _parse_choice_values(choice: str) -> List[float]:
                cl = (choice or "").lower()
                vals: List[float] = []

                # inequalities and ranges
                # e.g. "lớn hơn 2,5" / "nhỏ hơn 3" / "từ 1 đến 2"
                m = re.search(r"lớn hơn\s*(\d+(?:[\.,]\d+)?)", cl)
                if m:
                    vals.append(_to_float(m.group(1)))
                m = re.search(r"nhỏ hơn\s*(\d+(?:[\.,]\d+)?)", cl)
                if m:
                    vals.append(_to_float(m.group(1)))
                m = re.search(r"từ\s*(\d+(?:[\.,]\d+)?)\s*đến\s*(\d+(?:[\.,]\d+)?)", cl)
                if m:
                    vals.append(_to_float(m.group(1)))
                    vals.append(_to_float(m.group(2)))

                # fractions like 20/3 inside choices
                for fm in re.finditer(r"([-+]?\d+(?:[\.,]\d+)?)\s*/\s*(\d+(?:[\.,]\d+)?)", cl):
                    a = _to_float(fm.group(1))
                    b = _to_float(fm.group(2))
                    if b != 0:
                        vals.append(a / b)

                # generic numbers (also covers scientific notation)
                for nm in re.findall(r"[-+]?\d+(?:[\.,]\d+)?(?:e[-+]?\d+)?", cl):
                    try:
                        vals.append(_to_float(nm))
                    except Exception:
                        continue

                # de-duplicate while preserving order
                out: List[float] = []
                seen = set()
                for v in vals:
                    key = round(v, 12)
                    if key in seen:
                        continue
                    seen.add(key)
                    out.append(v)
                return out

            calculated_val = _extract_result_value(result)
            if calculated_val is None:
                return None

            best_idx = -1
            min_diff = float("inf")

            # First: handle range/inequality choices explicitly
            for i, choice in enumerate(choices):
                cl = (choice or "").lower()
                rng = re.search(r"từ\s*(\d+(?:[\.,]\d+)?)\s*đến\s*(\d+(?:[\.,]\d+)?)", cl)
                if rng:
                    lo = _to_float(rng.group(1))
                    hi = _to_float(rng.group(2))
                    if lo <= calculated_val <= hi:
                        return chr(65 + i)

                gt = re.search(r"lớn hơn\s*(\d+(?:[\.,]\d+)?)", cl)
                if gt and calculated_val > _to_float(gt.group(1)):
                    return chr(65 + i)

                lt = re.search(r"nhỏ hơn\s*(\d+(?:[\.,]\d+)?)", cl)
                if lt and calculated_val < _to_float(lt.group(1)):
                    return chr(65 + i)

            # NEW: Try Vietnamese number parsing first
            for i, choice in enumerate(choices):
                vn_num = self._parse_vietnamese_number(choice)
                if vn_num is not None:
                    diff = abs(calculated_val - vn_num)
                    # Use stricter tolerance for Vietnamese numbers
                    tol_vn = max(1, 0.01 * abs(calculated_val))
                    if diff < tol_vn and diff < min_diff:
                        min_diff = diff
                        best_idx = i

            # Second: closest numeric match (original logic)
            for i, choice in enumerate(choices):
                vals = _parse_choice_values(choice)
                if not vals:
                    continue
                # choose the value in this option that best matches
                local_best = min(abs(calculated_val - v) for v in vals)
                if local_best < min_diff:
                    min_diff = local_best
                    best_idx = i

            if best_idx >= 0:
                tol = max(1e-3, 0.02 * abs(calculated_val))
                # allow slightly larger absolute tolerance for very small numbers
                tol = max(tol, 0.05)
                if min_diff <= tol:
                    return chr(65 + best_idx)

            # Fallback: string containment for exact printed outputs
            for i, choice in enumerate(choices):
                if result and result.strip() and result.strip() in (choice or ""):
                    return chr(65 + i)

            return None
            
        except Exception as e:
            print(f"Error matching choice: {e}")
            return None
