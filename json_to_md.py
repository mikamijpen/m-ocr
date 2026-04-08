import json
import os


def _extract_page_number_from_filename(path):
    base = os.path.basename(path)
    digits = "".join(ch for ch in base if ch.isdigit())
    if digits:
        try:
            return int(digits)
        except ValueError:
            return None
    return None


def _sort_blocks_japanese_reading_order(blocks):
    """Sort blocks in a manga-friendly order.

    Strategy:
    - Group blocks into tiers by Y-range overlap (top-to-bottom tiers).
    - Within each tier, sort right-to-left by X (using xmax).
    """

    if not blocks:
        return []

    def safe_box(block):
        box = block.get("box") or []
        if len(box) >= 4:
            try:
                x1 = float(box[0])
                y1 = float(box[1])
                x2 = float(box[2])
                y2 = float(box[3])
                return x1, y1, x2, y2
            except (TypeError, ValueError):
                pass
        return 0.0, 0.0, 0.0, 0.0

    sorted_by_ymin = sorted(blocks, key=lambda b: safe_box(b)[1])
    tiers = []
    current_tier = []
    current_tier_ymax = None

    for block in sorted_by_ymin:
        _, ymin, _, ymax = safe_box(block)

        if not current_tier:
            current_tier.append(block)
            current_tier_ymax = ymax
            continue

        if ymin <= (current_tier_ymax if current_tier_ymax is not None else ymax):
            current_tier.append(block)
            current_tier_ymax = max(current_tier_ymax, ymax)
        else:
            tiers.append(current_tier)
            current_tier = [block]
            current_tier_ymax = ymax

    if current_tier:
        tiers.append(current_tier)

    final_sorted_blocks = []
    for tier in tiers:
        tier_sorted = sorted(tier, key=lambda b: safe_box(b)[2], reverse=True)
        final_sorted_blocks.extend(tier_sorted)

    return final_sorted_blocks


def _iter_pages_from_json_data(data):
    if isinstance(data, dict) and isinstance(data.get("pages"), list):
        for page in data.get("pages", []):
            yield page
        return

    if isinstance(data, dict) and isinstance(data.get("blocks"), list):
        yield data
        return

    yield {"blocks": []}

def extract_text_to_markdown(input_path, output_md_path):
    if not os.path.exists(input_path):
        print(f"❌ 找不到输入路径: {input_path}")
        return

    json_files = []
    if os.path.isdir(input_path):
        for name in os.listdir(input_path):
            if name.lower().endswith(".json"):
                json_files.append(os.path.join(input_path, name))

        json_files.sort(key=lambda p: (_extract_page_number_from_filename(p) is None,
                                       _extract_page_number_from_filename(p) or 0,
                                       os.path.basename(p)))
    else:
        json_files = [input_path]

    md_lines = []
    page_counter = 0

    for json_path in json_files:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for page in _iter_pages_from_json_data(data):
            page_counter += 1
            md_lines.append(f"## 第 {page_counter} 页\n")

            blocks = page.get("blocks", [])
            blocks = _sort_blocks_japanese_reading_order(blocks)

            if not blocks:
                md_lines.append("*（本页无文字）*\n\n")
                continue

            for block in blocks:
                lines = block.get("lines", [])
                block_text = "".join(lines)
                if block_text.strip():
                    md_lines.append(f"- {block_text}\n")

            md_lines.append("\n")

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)

    print(f"✅ 提取完成！Markdown 文件已保存至: {output_md_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="JSON 文件路径，或包含多个 per-page JSON 的文件夹路径")
    parser.add_argument("output", nargs="?", default="manga_text.md", help="输出 Markdown 文件路径")
    args = parser.parse_args()

    extract_text_to_markdown(args.input, args.output)