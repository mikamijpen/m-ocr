import os
os.environ["XDG_DATA_HOME"] = "/mnt/datasets/lyl_model"

os.environ["HF_HOME"] = "/mnt/datasets/lyl_model/hug"

import subprocess
import json
from pdf2image import convert_from_path



def process_manga_pdf(pdf_path, output_dir="manga_pages"):
    # 1. 创建存放图片的目录
    os.makedirs(output_dir, exist_ok=True)

    # 2. 将 PDF 转为图片
    print(f"正在将 {pdf_path} 转换为图片...")
    pages = convert_from_path(pdf_path, dpi=300)
    for i, page in enumerate(pages):
        # 补零命名，如 page_001.jpg，保证处理顺序
        img_path = os.path.join(output_dir, f"page_{i+1:03d}.jpg")
        page.save(img_path, "JPEG")
    print(f"PDF 转换完成，共 {len(pages)} 页。")

    # 3. 调用 Mokuro 进行端到端处理 (文字框检测 + Manga OCR)
    print("正在启动 Mokuro 进行文字检测与识别 (首次运行会自动下载检测模型，请保持网络通畅)...")
    
    # 使用 python -m mokuro 确保能正确调用
    subprocess.run(["python", "-m", "mokuro", output_dir])

    print("=======================================")
    print(f"处理完成！")
    print(f"你的 JSON 结果文件保存在: {output_dir}.json")

if __name__ == "__main__":
    # 把这里替换成你的 PDF 文件名
    input_pdf = "fuji2-004-006.pdf"  
    
    # 执行流水线
    process_manga_pdf(input_pdf, output_dir="manga_pages")