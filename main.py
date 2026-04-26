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
        font_path: str = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        bg_color: str = "white",
        text_color: str = "black"
):
    """
    文字转图片（保留原始空格与换行，自动换行适应宽度，支持彩色 Emoji）
    """
    # 1. 加载普通文字字体
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        logger.warning(f"字体加载失败，使用默认字体：{e}")
        font = ImageFont.load_default(size=font_size)

    usable_width = max_width - 40

    # 2. 按原始换行分段
    paragraphs = text.split('\n')

    lines = []
    line_height = int(1.4 * font_size) + 1

    for para in paragraphs:
        if para == '':
            lines.append('')
            continue

        current_line = ''
        current_width = 0.0
        for char in para:
            char_width = font.getlength(char)

            # 关键修复：如果字体无法测量该字符（例如 Emoji），赋予估计宽度
            if char_width <= 0:
                char_width = font_size  # emoji 通常为正方形，宽度约等于字号

            if current_width + char_width > usable_width:
                lines.append(current_line)
                current_line = char
                current_width = char_width
            else:
                current_line += char
                current_width += char_width

        if current_line:
            lines.append(current_line)

    # 3. 计算高度
    total_height = 20 + len(lines) * line_height + 20

    # 4. 绘制
    img = Image.new("RGB", (max_width, total_height), bg_color)

    with Pilmoji(img) as pilmoji:
        y = 20
        for line in lines:
            if line != '':
                pilmoji.text((20, y), line, fill=text_color, font=font)
            y += line_height

    img.save(output_path)
    logger.info(f"图片已生成：{output_path}（宽度：{max_width}px）")