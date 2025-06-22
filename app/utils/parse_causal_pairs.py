import re

def extract_causal_pairs(text: str):
    """
    仮説文から「原因 → 結果」のペアを抽出（ルールベース）
    """
    results = []
    sentences = re.split(r'[。．]', text)
    for sentence in sentences:
        # 「〜が〜を引き起こす」「〜によって〜が発生した」などのパターン
        patterns = [
            r"(.*?)が(.*?)を引き起こす",
            r"(.*?)が(.*?)をもたらす",
            r"(.*?)によって(.*?)が発生",
            r"(.*?)の結果、(.*?)が生じ",
            r"(.*?)のため(.*?)が発生",
        ]
        for pat in patterns:
            match = re.search(pat, sentence)
            if match:
                cause = match.group(1).strip()
                effect = match.group(2).strip()
                results.append((cause, effect))
    return results
