from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip

# 视频文件和水印图片路径
video_path = '1.mp4'
watermark_path = 'test.png'  # 确保这是透明背景的 PNG 图片

# 加载视频文件
video_clip = VideoFileClip(video_path)

# 获取视频尺寸
video_width, video_height = video_clip.size

# 加载水印图片
# resize() 功能需要直接传递元组作为参数来调整尺寸大小
# 我们这里按照视频宽度的5%来设置水印的大小，并保持水印原有的宽高比
watermark_clip = (ImageClip(watermark_path)
                  # .resize(width=video_width * 0.05)  # 可以直接指定新的宽度
                  .set_duration(video_clip.duration)
                  .set_position(("right", "bottom")))  # 设置水印位置

# 在视频上叠加水印图片并输出
final_clip = CompositeVideoClip([video_clip, watermark_clip], size=video_clip.size)

output_path = 'output_with_watermark.mp4'
final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
