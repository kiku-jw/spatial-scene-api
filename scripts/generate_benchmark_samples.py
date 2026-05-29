from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


OUTPUT_DIR = Path("samples/benchmark")
WIDTH = 1400
HEIGHT = 1000


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _portrait_card(OUTPUT_DIR / "portrait_card.png")
    _product_label(OUTPUT_DIR / "product_label.png")
    _interior_depth(OUTPUT_DIR / "interior_depth.png")
    _wide_landscape(OUTPUT_DIR / "wide_landscape.png")
    _typography_poster(OUTPUT_DIR / "typography_poster.png")
    _food_table(OUTPUT_DIR / "food_table.png")
    _city_layers(OUTPUT_DIR / "city_layers.png")
    _abstract_shapes(OUTPUT_DIR / "abstract_shapes.png")
    print(f"Wrote benchmark samples to {OUTPUT_DIR}")


def _canvas(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), top)
    draw = ImageDraw.Draw(image)
    for y_position in range(HEIGHT):
        progress = y_position / max(1, HEIGHT - 1)
        color = tuple(
            int(top[channel] * (1.0 - progress) + bottom[channel] * progress)
            for channel in range(3)
        )
        draw.line([(0, y_position), (WIDTH, y_position)], fill=color)
    return image


def _portrait_card(path: Path) -> None:
    image = _canvas((222, 228, 223), (185, 191, 183))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 690, WIDTH, HEIGHT], fill=(70, 91, 82))
    draw.ellipse([470, 190, 930, 760], fill=(238, 188, 122))
    draw.ellipse([575, 85, 820, 335], fill=(238, 204, 164))
    draw.rectangle([550, 485, 850, 905], fill=(38, 86, 73))
    draw.rectangle([610, 690, 685, 980], fill=(48, 67, 87))
    draw.rectangle([720, 690, 795, 980], fill=(48, 67, 87))
    draw.ellipse([615, 175, 645, 205], fill=(41, 37, 34))
    draw.ellipse([750, 175, 780, 205], fill=(41, 37, 34))
    draw.arc([635, 205, 775, 285], start=25, end=155, fill=(94, 55, 48), width=6)
    draw.rectangle([85, 110, 440, 245], fill=(248, 246, 239))
    draw.text((128, 150), "CREATOR PORTRAIT", fill=(30, 34, 31))
    _save(image, path)


def _product_label(path: Path) -> None:
    image = _canvas((232, 232, 226), (208, 212, 206))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 725, WIDTH, HEIGHT], fill=(82, 96, 88))
    draw.polygon([(440, 245), (920, 165), (1035, 695), (515, 800)], fill=(191, 93, 68))
    draw.polygon([(440, 245), (515, 800), (330, 640), (265, 180)], fill=(142, 65, 55))
    draw.polygon([(440, 245), (920, 165), (760, 80), (265, 180)], fill=(221, 128, 82))
    draw.rectangle([500, 370, 930, 560], fill=(248, 244, 231))
    draw.text((548, 415), "NO AI MUTATIONS", fill=(32, 34, 31))
    draw.text((548, 470), "SPATIAL VIDEO API", fill=(32, 34, 31))
    draw.rectangle([610, 605, 790, 655], fill=(42, 80, 96))
    _save(image, path)


def _interior_depth(path: Path) -> None:
    image = _canvas((219, 223, 218), (189, 184, 176))
    draw = ImageDraw.Draw(image)
    draw.polygon([(0, 760), (WIDTH, 760), (WIDTH, HEIGHT), (0, HEIGHT)], fill=(134, 118, 104))
    draw.line([(WIDTH // 2, 395), (0, 760)], fill=(164, 155, 145), width=6)
    draw.line([(WIDTH // 2, 395), (WIDTH, 760)], fill=(164, 155, 145), width=6)
    draw.rectangle([180, 210, 500, 620], fill=(61, 91, 106))
    draw.rectangle([218, 250, 462, 585], fill=(149, 185, 194))
    draw.rectangle([805, 320, 1190, 680], fill=(212, 205, 191))
    draw.rectangle([855, 375, 1145, 635], fill=(88, 124, 105))
    draw.rectangle([470, 660, 950, 760], fill=(91, 68, 56))
    draw.ellipse([560, 540, 810, 695], fill=(229, 197, 125))
    _save(image, path)


def _wide_landscape(path: Path) -> None:
    image = _canvas((174, 207, 220), (231, 222, 188))
    draw = ImageDraw.Draw(image)
    draw.ellipse([1040, 95, 1190, 245], fill=(243, 190, 92))
    draw.polygon([(0, 620), (310, 300), (585, 620)], fill=(84, 109, 112))
    draw.polygon([(290, 640), (680, 230), (1080, 640)], fill=(67, 91, 102))
    draw.polygon([(760, 650), (1120, 360), (WIDTH, 650)], fill=(95, 122, 116))
    draw.rectangle([0, 650, WIDTH, 790], fill=(79, 132, 142))
    draw.rectangle([0, 790, WIDTH, HEIGHT], fill=(86, 112, 83))
    draw.rectangle([500, 735, 950, 775], fill=(246, 238, 203))
    draw.text((548, 742), "WIDE SHOT", fill=(36, 38, 34))
    _save(image, path)


def _typography_poster(path: Path) -> None:
    image = _canvas((238, 236, 229), (204, 207, 201))
    draw = ImageDraw.Draw(image)
    draw.rectangle([220, 110, 1180, 900], fill=(247, 246, 240))
    draw.rectangle([295, 190, 1105, 335], fill=(39, 49, 47))
    draw.text((350, 238), "TEXT MUST STAY TEXT", fill=(246, 244, 235))
    draw.rectangle([295, 395, 1105, 760], outline=(39, 49, 47), width=12)
    draw.text((360, 500), "API-FIRST PARALLAX", fill=(39, 49, 47))
    draw.text((360, 575), "NO HALLUCINATIONS", fill=(39, 49, 47))
    _save(image, path)


def _food_table(path: Path) -> None:
    image = _canvas((224, 220, 205), (185, 170, 145))
    draw = ImageDraw.Draw(image)
    draw.ellipse([150, 450, 1260, 970], fill=(118, 77, 52))
    draw.ellipse([430, 230, 980, 790], fill=(246, 239, 220))
    draw.ellipse([520, 315, 900, 695], fill=(206, 93, 68))
    draw.ellipse([610, 420, 810, 620], fill=(242, 190, 92))
    draw.rectangle([1045, 270, 1190, 760], fill=(48, 86, 78))
    draw.rectangle([1065, 200, 1170, 310], fill=(230, 230, 218))
    draw.text((535, 795), "FOOD PRODUCT TEST", fill=(246, 239, 220))
    _save(image, path)


def _city_layers(path: Path) -> None:
    image = _canvas((190, 208, 216), (219, 214, 198))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 740, WIDTH, HEIGHT], fill=(85, 84, 78))
    colors = [(112, 125, 132), (73, 91, 104), (45, 64, 78)]
    for layer_index, color in enumerate(colors):
        offset = layer_index * 90
        for x_position in range(-80 + offset, WIDTH, 170):
            top = 420 - layer_index * 70 + (x_position % 3) * 18
            draw.rectangle([x_position, top, x_position + 118, 760], fill=color)
            draw.rectangle([x_position + 24, top + 42, x_position + 55, top + 95], fill=(225, 208, 125))
    draw.rectangle([560, 625, 940, 735], fill=(238, 236, 222))
    draw.text((610, 662), "CITY LAYERS", fill=(37, 40, 38))
    _save(image, path)


def _abstract_shapes(path: Path) -> None:
    image = _canvas((226, 229, 222), (199, 204, 195))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 730, WIDTH, HEIGHT], fill=(75, 91, 85))
    draw.ellipse([240, 205, 690, 655], fill=(45, 93, 110))
    draw.rectangle([655, 255, 1095, 695], fill=(213, 105, 73))
    draw.polygon([(735, 120), (1195, 430), (880, 820)], fill=(234, 187, 91))
    draw.rectangle([345, 700, 1050, 770], fill=(247, 244, 230))
    draw.text((420, 722), "AI ART SHAPE TEST", fill=(34, 37, 34))
    _save(image, path)


def _save(image: Image.Image, path: Path) -> None:
    image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=2))
    image.save(path)


if __name__ == "__main__":
    main()
