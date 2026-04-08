# m-ocr
提取日语漫画

 sudo apt-get install poppler-utils
 # 创建虚拟环境
conda create -n manga_pipeline python=3.10
conda activate manga_pipeline

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
降级兼容.pt
pip install transformers==4.46.3 huggingface_hub==0.26.2

dif已有
# 安装提取工具 
pip install mokuro pdf2image

git clone https://github.com/zyddnys/comic-text-detector.git

python manga_extractor.py

可以改路径
~/.local/share/mokuro/
~/.cache/huggingface/hub/

python json_to_md.py ./_ocr/manga_pages output.md