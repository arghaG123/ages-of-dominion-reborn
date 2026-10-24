from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[3]
scene_dir = root / "qa/game-completion-20261020/visual-review/kingdom-live"
cards = []
for age in range(8):
    image = Image.open(scene_dir / f"age-{age}-adventure-825x375.png").convert("RGB")
    image.thumbnail((400, 182), Image.Resampling.LANCZOS)
    cards.append((image.copy(), Image.open(scene_dir / f"age-{age}-adventure-825x375.png").size))

label_height = 26
card_width = 400
card_height = 182 + label_height
sheet = Image.new("RGB", (card_width * 4, card_height * 2), "#111820")
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
ages = ["Stone", "Bronze", "Iron", "Medieval", "Gunpowder", "Industrial", "Modern", "Future"]
for index, (image, _) in enumerate(cards):
    x = (index % 4) * card_width
    y = (index // 4) * card_height
    sheet.paste(image, (x, y))
    draw.rectangle((x, y + 182, x + card_width, y + card_height), fill="#111820")
    draw.text((x + 9, y + 186), ages[index] + " Age · 825×375", fill="#efe5d3", font=font)

output = root / "qa/game-completion-20261020/visual-review/adventure-eight-ages-natural-825x375-contact-20261020.jpg"
sheet.save(output, quality=92)
print(output)
