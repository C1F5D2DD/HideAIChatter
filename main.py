from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger # 使用 astrbot 提供的 logger 接口
import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig
from astrbot.api.provider import ProviderRequest

from PIL import Image, ImageDraw, ImageFont
import os




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

                text_to_image(text=message.text,
                              output_path=self.config.output_path,
                              font_path=self.config.font_path,
                              max_width=self.config.max_width,
                              font_size=self.config.font_size)

               # print("processing: ", messages.text)
                chain2.append(Comp.Image.fromURL('https://localhost/tmp/hider.png'))
                #url = await self.text_to_image(message.text)
                #chain2.append(Comp.Image.fromURL(url=url))
            else:
                chain2.append(message)
        #chain2.append(Comp.Plain("!!!!!!!!!!!!!!!!"))
        result.chain=chain2.copy()

    @filter.on_llm_request()
    async def my_custom_hook_1(self, event: AstrMessageEvent, req: ProviderRequest):  # 请注意有三个参数
        print(req)  # 打印请求的文本
        req.system_prompt += "/no_think" if self.config.no_think else ""


def text_to_image(
    text: str,
    output_path: str = '/var/www/html/tmp/hider.png',
    max_width: int = 400,  # 图片最大宽度
    font_size: int = 20,   # 字体大小
    font_path: str = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    bg_color: str = "white",  # 背景色（支持颜色名/十六进制）
    text_color: str = "black" # 文字色
):
    """
    文字转图片（限制宽度+自动换行+兼容中文/英文/Emoji）
    :param text: 要转换的文字（支持中文、英文、Emoji）
    :param output_path: 输出图片路径
    :param max_width: 图片最大宽度（像素）
    :param font_size: 字体大小
    :param font_path: 字体路径（Linux Noto CJK 字体）
    :param bg_color: 背景色（如 "white"、"#f0f0f0"）
    :param text_color: 文字色（如 "black"、"#333333"）
    """
    os.remove(output_path)

    # 1. 加载字体（启用多字符集排版引擎）
    try:
        font = ImageFont.truetype(
            font_path, font_size
        )
    except Exception as e:
        print(f"字体加载失败，使用默认字体：{e}")
        font = ImageFont.load_default(size=font_size)

    # 2. 自动换行（按空格拆分，适配宽度）
    lines=[]
    chars = list(text)
    current_line = ""
    line_width = 0
    for char in chars:
        # 获取文字宽度
        char_width = font.getlength(char)
        line_width+=char_width
        if (line_width <= max_width - 40) and (char != chars[-1]):  # 留20px左右内边距
            current_line =current_line + char
        else:
            if char != chars[-1]:
                current_line = current_line + char
            lines.append(current_line)
            current_line = ''
            line_width = 0
    # 3. 计算图片高度（行高=字号+8px间距）
    line_height = int(1.4*font_size)
    total_height = line_height * len(lines) + 40  # 上下各20px内边距

    # 4. 创建图片并绘制文字
    img = Image.new("RGB", (max_width, total_height), bg_color)
    draw = ImageDraw.Draw(img)
    y = 20  # 文字起始y坐标（顶部内边距）
    for line in lines:
        draw.text((20, y), line, fill=text_color, font=font)
        y += line_height

    # 5. 保存图片
    img.save(output_path)
    print(f"图片已生成：{output_path}（宽度：{max_width}px）")