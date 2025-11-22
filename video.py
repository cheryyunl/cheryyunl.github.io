import os
from moviepy.editor import VideoFileClip, ImageClip, clips_array
from PIL import Image
import numpy as np

# ================= 高画质配置区域 =================
# 1. 截取时长 (秒)：建议 2.5 - 3.0 秒
CLIP_DURATION = 2.5 

# 2. 宽度 (像素)：500 是清晰度和体积的平衡点
TOTAL_WIDTH = 700 

# 3. 帧率 (FPS)：降到 10，为了把文件体积留给画质
FPS = 10
# ==============================================

def process_transparent_png(png_path, target_width):
    """高质量图片缩放"""
    try:
        img = Image.open(png_path)
    except Exception as e:
        print(f"无法打开图片 {png_path}: {e}")
        return None

    # 计算高度
    w_percent = (target_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    
    # 关键：使用 LANCZOS 算法进行高质量缩放，抗锯齿
    img = img.resize((target_width, h_size), Image.Resampling.LANCZOS)
    
    # 处理透明背景
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[3])
        img = background
    else:
        img = img.convert("RGB")
    
    return np.array(img)

def get_middle_clip(video_path, duration_needed, target_width):
    if not os.path.exists(video_path):
        print(f"❌ 找不到文件: {video_path}")
        return None
        
    clip = VideoFileClip(video_path)
    
    # 智能截取中间段
    if clip.duration > duration_needed:
        start_time = (clip.duration - duration_needed) / 2
        end_time = start_time + duration_needed
        clip = clip.subclip(start_time, end_time)
        
    # 使用 resize 缩放视频
    return clip.resize(width=target_width).without_audio()

def create_hd_gif(top_img_path, all_videos, output_name):
    print("🚀 开始生成高画质 GIF...")
    
    # --- 1. 视频处理 (取第1和第3个) ---
    # 确保你的列表里至少有3个视频
    selected_videos = [all_videos[0], all_videos[2]]
    
    processed_clips = []
    cell_width = TOTAL_WIDTH // 2 

    for v_path in selected_videos:
        clip = get_middle_clip(v_path, CLIP_DURATION, cell_width)
        if clip:
            processed_clips.append(clip)
            
    # --- 2. 拼接底部 ---
    bottom_row = clips_array([ processed_clips ])

    # --- 3. 图片处理 ---
    top_img_array = process_transparent_png(top_img_path, TOTAL_WIDTH)
    if top_img_array is None: return
    
    top_clip = ImageClip(top_img_array)
    top_clip = top_clip.set_duration(bottom_row.duration)

    # --- 4. 最终堆叠 ---
    final_clip = clips_array([
        [top_clip],
        [bottom_row]
    ])

    # --- 5. 导出 (关键修改) ---
    print(f"💾 正在渲染 (画质优先模式)...")
    final_clip.write_gif(
        output_name,
        fps=FPS,
        program='ffmpeg',
        opt='optimizeplus', # 保持优化算法
        fuzz=0,      # 关键修改：设为 0，禁止模糊颜色，文字会变清晰
        colors=256   # 关键修改：设为 256，使用 GIF 最大色深
    )
    print(f"✅ 完成！请检查: {output_name}")

if __name__ == "__main__":
    # 你的文件路径
    top_image = "images/moma.png" 
    videos = ["/Users/cheryunl/Downloads/1.mp4", "/Users/cheryunl/Downloads/2.mp4", "/Users/cheryunl/Downloads/3.mp4", "/Users/cheryunl/Downloads/4.mp4"] 
    
    create_hd_gif(top_image, videos, "result_high_quality.gif")