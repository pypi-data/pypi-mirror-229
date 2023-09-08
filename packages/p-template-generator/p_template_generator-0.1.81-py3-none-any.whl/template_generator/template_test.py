import sys
import os
import subprocess
import json
import shutil
import zipfile
from template_generator import template
from template_generator import binary

def updateRes(rootDir):
    for root,dirs,files in os.walk(rootDir):
        for file in files:
            if file.find(".") <= 0:
                continue
            name = file[0:file.index(".")]
            ext = file[file.index("."):]
            if ext == ".zip.py" and os.path.exists(os.path.join(root, name)) == False:
                for dir in dirs:
                    shutil.rmtree(os.path.join(root, dir))
                with zipfile.ZipFile(os.path.join(root, file), "r") as zipf:
                    zipf.extractall(os.path.join(root, name))
                return
        if root != files:
            break

def test(searchPath):
    rootDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test")
    updateRes(rootDir)
    config = {
        "input":[
            os.path.join(rootDir, "res", "1.png"),
            os.path.join(rootDir, "res", "2.png"),
            os.path.join(rootDir, "res", "3.png"),
            os.path.join(rootDir, "res", "4.png"),
            ],
        "template":os.path.join(rootDir, "res", "tp"),
        "params":{},
        "output":os.path.join(rootDir, "res", "out.mp4")
        }
    with open(os.path.join(rootDir, "res", "param.config"), 'w') as f:
        json.dump(config, f)

    command = f'template --input {os.path.join(rootDir, "res", "param.config")}'
    print(f"test template command => {command}")
    cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while cmd.poll() is None:
        print(cmd.stdout.readline().rstrip().decode('utf-8'))

def psnr(target, ref, scale):
    target_data = np.array(target)
    target_data = target_data[scale:-scale,scale:-scale]
 
    ref_data = np.array(ref)
    ref_data = ref_data[scale:-scale,scale:-scale]
 
    diff = ref_data - target_data
    diff = diff.flatten('C')
    rmse = math.sqrt(np.mean(diff ** 2.) )
    return 20*math.log10(1.0/rmse)

# import cv2
# import numpy as np
# import math
# def calculate_psnr(original_img, compressed_img):
#     img1 = cv2.imread(original_img)
#     img2 = cv2.imread(compressed_img)

#     gray_img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#     gray_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#     mse = np.mean((gray_img1 - gray_img2) ** 2)

#     if mse == 0:
#         return float('inf')

#     max_pixel = 255.0
#     psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
#     return psnr

# from skimage.metrics import structural_similarity as compare_ssim
# def calculate_ssim(original_img, compressed_img):
#     img1 = cv2.imread(original_img)
#     img2 = cv2.imread(compressed_img)
#     gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#     gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#     score, diff = compare_ssim(gray1, gray2, full=True)
#     return score

# psnr_score = calculate_psnr("C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\heidao-shu_video-cover.jpg",
#                              "C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\mohu.jpg")
# print(f"================== PSNR分数为：{psnr_score:.2f}")
# psnr_score = calculate_psnr("C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out.png")
# print(f"================== PSNR分数为：{psnr_score:.2f}")
# psnr_score = calculate_psnr("C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out_stb.png")
# print(f"================== PSNR分数为：{psnr_score:.2f}")

# ssim_score = calculate_ssim("C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\heidao-shu_video-cover.jpg",
#                              "C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\mohu.jpg")
# print(f"================== SSIM分数为：{ssim_score:.2f}")
# ssim_score = calculate_ssim("C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out.png")
# print(f"================== SSIM分数为：{ssim_score:.2f}")
# ssim_score = calculate_ssim("C:\\Users\\123\\AppData\\Roaming\\VOO\\output\\heidao-shu\\heidao-shu_video-cover.jpg",
#                              "E:\\template\\111111111111111111111111111111111111111111package\\test\\out_stb.png")
# print(f"================== SSIM分数为：{ssim_score:.2f}")