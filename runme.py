import pyglet
from perlin_noise import PerlinNoise
import math
from pyglet.window import key

from pyglet import shapes

window = pyglet.window.Window(width = 1520, height = 680, resizable = True, caption="Stranded")

x = 0
y = 0

xMomentum = 0
yMomentum = 0

oxygen = 1

oxygenMinutes = 20
oxygenDepletePerSecond = 1 / (oxygenMinutes * 60)

pyglet.font.add_file("assets/fonts/Poppins-Regular.ttf")
pyglet.font.load("Poppins")

tileNames = {
    "mars": "assets/images/tiles/mars.png",
    "marsLight": "assets/images/tiles/marsLight.png"
}

tiles = {}

for tileName in tileNames:
    tilePath = tileNames[tileName]

    tiles[tileName] = pyglet.image.load(tilePath)

idleImage = pyglet.image.load("assets/images/player/astronautIdle.png")

playerWalkingStates = ["forward", "backward"]

playerImagesWalking = {}

for playerWalkingState in playerWalkingStates:
    playerImagesWalking[playerWalkingState] = pyglet.image.ImageGrid(
        pyglet.image.load("assets/images/player/astronautWalk_" + playerWalkingState + ".png"),
        1, 9)

tileSize = 256 # Pixels?

walkingFrame = 0

staticAssets = {
    "rocket": {
        "path": "rocket.png",
        "x": 0,
        "y": 0,
        "scale": tileSize
    }
}

staticAssetList = []

for staticAsset in staticAssets:
    staticAssetList.append({
        "image": pyglet.image.load("assets/images/static/" + staticAssets[staticAsset]["path"]),
        "x": staticAssets[staticAsset]["x"],
        "y": staticAssets[staticAsset]["y"],
        "scale": staticAssets[staticAsset]["scale"] / 1024
    })

noise = PerlinNoise(octaves = 1, seed = 1000)

@window.event
def on_draw():
    global walkingFrame, oxygen

    window.clear()

    offsetX = round(-x % tileSize)
    offsetY = round(y % tileSize / 1.5)
    
    for tileX in range(-3, round(window.width / tileSize * 2) + 1):
        for tileY in range(-2, round(window.height / tileSize * 1.5) + 1):
            tileWorldX = tileX / 2 + math.ceil(x / tileSize)
            tileWorldY = tileY - math.ceil(y / tileSize)

            selectedImage = tiles["mars"]
            if noise([tileWorldX / 4, tileWorldY / 4]) > 0:
                selectedImage = tiles["marsLight"]
            sprite = pyglet.sprite.Sprite(img=selectedImage)
            sprite.x = tileX * tileSize / 2 + offsetX
            if tileX % 2 == 0:
                sprite.y = tileY * tileSize / 1.5 + offsetY
            else:
                sprite.y = tileY * tileSize / 1.5 + tileSize / 1.5 / 2 + offsetY
            sprite.scale = tileSize / 1024

            sprite.draw() # Draw sprite

    for staticAsset in staticAssetList:
        if y >= staticAsset["y"]:
            sprite = pyglet.sprite.Sprite(img = staticAsset["image"])
            sprite.x = staticAsset["x"] - round(x)
            sprite.y = staticAsset["y"] + round(y / 1.5)

            sprite.scale = staticAsset["scale"]

            sprite.draw()

    playerImagePicked = idleImage
    
    if yMomentum < -0.5:
        playerImagePicked = playerImagesWalking["forward"][round(walkingFrame) % 9]
        walkingFrame += yMomentum / 25
    elif yMomentum > 0.5:
        playerImagePicked = playerImagesWalking["backward"][round(walkingFrame) % 9]
        walkingFrame += yMomentum / 25
    else:
        walkingFrame = 0

    playerImage = pyglet.sprite.Sprite(img=playerImagePicked)
    playerImage.x = window.width / 2 - tileSize / 4
    playerImage.y = window.height / 2 - tileSize / 2
    playerImage.scale = tileSize / 2048

    playerImage.draw()

    
    for staticAsset in staticAssetList:
        if y < staticAsset["y"]:
            sprite = pyglet.sprite.Sprite(img = staticAsset["image"])
            sprite.x = staticAsset["x"] - round(x)
            sprite.y = staticAsset["y"] + round(y / 1.5)

            sprite.scale = staticAsset["scale"]

            sprite.draw()

    UIBars = [
        {
            "name": "Oxygen",
            "value": oxygen,
            "countdown": True,
            "countdownTime": oxygen / oxygenDepletePerSecond
        }
    ]

    index = 0

    for UIBar in UIBars:
        index += 1

        bar = shapes.Rectangle(
            x = window.width - 505,
            y = window.height - 55 * index,
            width = 500,
            height = 50,
            color = ( 100, 100, 100 )
        )
        bar.opacity = 200
        bar.draw()

        filled = shapes.Rectangle(
            x = window.width - 500,
            y = window.height - 55 * index + 5,
            width = 490 * UIBar["value"],
            height = 40,
            color = ( 25, 100, 25 )
        )
        filled.draw()

        label = pyglet.text.Label(UIBar["name"],
            font_name = "Poppins",
            font_size = 25,
            x = window.width - 495,
            y = window.height - 5 - (55 * (index - 1)),
            color = (255, 255, 255, 255),
            anchor_x = "left", anchor_y = "top")
        label.draw()

        if UIBar["countdown"]:
            countdownTime = "{:0>2d}".format(math.floor(UIBar["countdownTime"] / 60)) + ":" + "{:0>2d}".format(math.floor(UIBar["countdownTime"]) % 60)
            countdown = pyglet.text.Label(countdownTime,
                font_name = "Poppins",
                font_size = 25,
                x = window.width - 10,
                y = window.height - 5 - (55 * (index - 1)),
                color = (255, 255, 255, 255),
                anchor_x = "right", anchor_y = "top")
            countdown.draw()


keysPressed = {
    "left": False,
    "right": False,
    "up": False,
    "down": False
}

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.LEFT:
        print("The left arrow key was pressed.")
        keysPressed["left"] = True
    elif symbol == key.RIGHT:
        print("The right arrow key was pressed.")
        keysPressed["right"] = True
    elif symbol == key.UP:
        print("The up arrow key was pressed.")
        keysPressed["up"] = True
    elif symbol == key.DOWN:
        print("The down arrow key was pressed.")
        keysPressed["down"] = True

@window.event
def on_key_release(symbol, modifiers):
    if symbol == key.LEFT:
        print("The left arrow key was released.")
        keysPressed["left"] = False
    elif symbol == key.RIGHT:
        print("The right arrow key was released.")
        keysPressed["right"] = False
    elif symbol == key.UP:
        print("The up arrow key was released.")
        keysPressed["up"] = False
    elif symbol == key.DOWN:
        print("The down arrow key was released.")
        keysPressed["down"] = False

from pyglet.window import mouse

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        print("The left mouse button was pressed.")

# Logs all events that happen
# event_logger = pyglet.window.event.WindowEventLogger()
# window.push_handlers(event_logger)


framerate = 144 # Frames per second

def update(dt):
    global x, y, xMomentum, yMomentum, oxygen

    movementSpeed = 60 * dt

    oxygenDepletionRate = oxygenDepletePerSecond * ((math.sqrt(xMomentum * xMomentum + yMomentum * yMomentum) + 25) / 25)

    oxygen -= oxygenDepletionRate * dt

    if(keysPressed["left"]):
        xMomentum -= movementSpeed
    if(keysPressed["right"]):
        xMomentum += movementSpeed
    if(keysPressed["up"]):
        yMomentum -= movementSpeed
    if(keysPressed["down"]):
        yMomentum += movementSpeed

    x += xMomentum
    y += yMomentum

    xMomentum /= 1.05
    yMomentum /= 1.05

    if math.fabs(xMomentum) < 0.5:
        xMomentum = 0
    if math.fabs(yMomentum) < 0.5:
        yMomentum = 0

pyglet.clock.schedule_interval(update, 1 / framerate)

pyglet.app.run()