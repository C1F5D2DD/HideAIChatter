from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger # 使用 astrbot 提供的 logger 接口
import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig
from astrbot.api.provider import ProviderRequest

import os
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji




class HideAIChatter(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        logger.info(f"running config:{config}")

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        logger.info(f"running config:{self.config}")
        result = event.get_result()
        chain = result.chain
        print(chain)  # 打印消息链
        chain2=[]
        for message in chain:
            if type(message) is Comp.Plain:
                if self.config.use_official_t2i:
                    url = await self.html_render(self.config.TMPL, eval(self.config.Jinja2), options=eval(self.config.options))
                    hain2.append(Comp.Image.fromURL(url))
                else:
                    text_to_image(text=message.text,
                                output_path=self.config.output_path,
                                font_path=self.config.font_path,
                                 max_width=self.config.max_width,
                                font_size=self.config.font_size)

                     # print("processing: ", messages.text)

                    chain2.append(Comp.Image.fromFileSystem(self.config.output_path))
                    #url = await self.text_to_image(message.text)
                    #chain2.append(Comp.Image.fromURL(url=url))
            else:
                chain2.append(message)
        #chain2.append(Comp.Plain("!!!!!!!!!!!!!!!!"))
        result.chain=chain2.copy()

    @filter.on_llm_request()
    async def no_think(self, event: AstrMessageEvent, req: ProviderRequest):  # 请注意有三个参数
        print(req)  # 打印请求的文本
        req.system_prompt += "/no_think" if self.config.no_think else ""


def text_to_image(
    text: str,
    output_path: str = '/var/www/html/tmp/hider.png',
    max_width: int = 400,
    font_size: int = 20,
    font_path: str = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", # 仅用于渲染普通文字
    bg_color: str = "white",
    text_color: str = "black"
):
    """
    文字转图片（保留原始空格与换行，自动换行适应宽度，支持彩色Emoji）

    行为：
    - 原始 \\n 视为强制换行（手动换行）
    - 每个自然段（原始换行分隔）内部，按像素宽度自动换行
    - 保留文本中所有空格（包括连续空格）
    - 左右各留 20px 内边距
    - 使用 pilmoji 自动调用系统Noto Color Emoji字体渲染彩色Emoji
    """
    # 1. 加载普通文字字体（pilmoji 会处理 emoji，无需单独加载）
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        logger.warning(f"字体加载失败，使用默认字体：{e}")
        font = ImageFont.load_default(size=font_size)

    # 2. 预留宽度（左右各 20px 边距）
    usable_width = max_width - 40

    # 3. 按原始换行分割为段落（保留所有原始换行逻辑）
    paragraphs = text.split('\n')

    lines = []               # 最终要绘制的每一行（包括空行）
    line_height = int(1.4 * font_size) + 1   # 行高

    for para in paragraphs:
        # 空段落表示一个空行（例如连续 \\n\\n）
        if para == '':
            lines.append('')
            continue

        # 对当前段落进行字符级自动换行
        current_line = ''
        current_width = 0.0
        for char in para:
            char_width = font.getlength(char)
            if current_width + char_width > usable_width:
                lines.append(current_line)
                current_line = char
                current_width = char_width
            else:
                current_line += char
                current_width += char_width
        # 处理段落最后一行
        if current_line:
            lines.append(current_line)

    # 4. 计算图片总高度
    total_height = 20 + len(lines) * line_height + 20

    # 5. 创建图片并绘制（使用 pilmoji 支持彩色 emoji）
    img = Image.new("RGB", (max_width, total_height), bg_color)

    with Pilmoji(img) as pilmoji:
        y = 20
        for line in lines:
            if line != '':
                # pilmoji.text 会自动处理文本中的emoji，而其他文字仍使用'font'参数指定的字体
                pilmoji.text((20, y), line, fill=text_color, font=font)
            y += line_height

    # 6. 保存图片
    img.save(output_path)
    logger.info(f"图片已生成：{output_path}（宽度：{max_width}px）")