from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger # 使用 astrbot 提供的 logger 接口
import astrbot.api.message_components as Comp


from PIL import Image, ImageDraw, ImageFont
import os




class HideAIChatter(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        chain = result.chain
        print(chain)  # 打印消息链
        for messages in chain:
            if type(messages) is Comp.Plain:
                text_to_image(messages.text)
               # print("processing: ", messages.text)
                chain.append(Comp.fromURL('https://localhost/tmp/hider.png'))
        chain.append(Comp.Plain("!!!!!!!!!!!!!!!!"))



def text_to_image(
        text: str,
        output_path: str = "/var/www/html/tmp/hider.png",
        font_path: str ='/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        font_size: int = 24,
        bg_color: tuple = (255, 255, 255),  # 白色背景 (R, G, B)
        text_color: tuple = (0, 0, 0),  # 黑色文字
        padding: int = 30,  # 文字与画布边缘的间距
        line_spacing: int = 10  # 行间距
):
    """
    将文字转换为图片（基于Pillow库）
    :param text: 要转换的文字（支持\n换行）
    :param output_path: 输出图片路径
    :param font_path: 字体文件路径（None则使用默认字体）
    :param font_size: 字体大小
    :param bg_color: 背景色，RGB元组（如白色(255,255,255)）
    :param text_color: 文字色，RGB元组（如黑色(0,0,0)）
    :param padding: 内边距（像素）
    :param line_spacing: 行间距（像素）
    """
    # 1. 设置字体（优先使用指定字体，无则用默认）
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            # 使用PIL默认字体（兼容Windows/macOS/Linux）
            font = ImageFont.load_default(size=font_size)
    except Exception:
        # 兜底：强制使用默认字体（避免字体加载失败）
        font = ImageFont.load_default(size=font_size)

    # 2. 拆分文字为多行，计算文字总尺寸
    lines = text.split("\n")
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))  # 临时画布用于计算文字尺寸

    # 计算每行文字的宽度和高度
    line_sizes = []
    max_line_width = 0
    total_text_height = 0
    for line in lines:
        if line.strip() == "":  # 空行
            line_width, line_height = 0, font_size
        else:
            # 获取文字的边界框尺寸（(left, top, right, bottom)）
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]

        line_sizes.append((line_width, line_height))
        max_line_width = max(max_line_width, line_width)
        total_text_height += line_height + line_spacing

    # 减去最后一行多余的行间距
    total_text_height -= line_spacing

    # 3. 创建最终画布（文字尺寸 + 左右/上下内边距）
    canvas_width = max_line_width + 2 * padding
    canvas_height = total_text_height + 2 * padding
    image = Image.new("RGB", (canvas_width, canvas_height), bg_color)
    draw = ImageDraw.Draw(image)

    # 4. 逐行绘制文字
    current_y = padding  # 文字起始Y坐标
    for idx, line in enumerate(lines):
        if line.strip() == "":
            current_y += font_size + line_spacing
            continue

        line_width, line_height = line_sizes[idx]
        # 文字水平居中（也可改为左对齐：x=padding）
        current_x = (canvas_width - line_width) // 2
        # 绘制文字
        draw.text(
            (current_x, current_y),
            line,
            fill=text_color,
            font=font,
            anchor="lt"  # 锚点：左上对齐（避免文字偏移）
        )
        current_y += line_height + line_spacing

    # 5. 保存图片
    image.save(output_path)
    print(f"图片已保存至：{os.path.abspath(output_path)}")


# ------------------- 测试用例 -------------------
