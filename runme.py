import pyglet
from perlin_noise import PerlinNoise
import math
from pyglet.window import key

from pyglet import shapes

import random

window = pyglet.window.Window(width = 1520, height = 680, resizable = True, caption="Stranded")

x = 0
y = 0

xMomentum = 0
yMomentum = 0

oxygen = 1

oxygenMinutes = 20
oxygenDepletePerSecond = 1 / (oxygenMinutes * 60)

gameState = "intro"
introElapsed = 0

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

starCount = 80

stars = []

shipPath = [
    { "x": 0.74, "y": 0.820 },
    { "x": 0.72, "y": 0.870 },
    { "x": 0.70, "y": 0.900 },
    { "x": 0.68, "y": 0.930 },
    { "x": 0.66, "y": 0.950 },
    { "x": 0.64, "y": 0.970 },
    { "x": 0.62, "y": 0.980 },
    { "x": 0.60, "y": 0.988 },
    { "x": 0.58, "y": 0.990 },
    { "x": 0.56, "y": 0.995 },
    { "x": 0.54, "y": 0.993 },
    { "x": 0.52, "y": 0.991 },
    { "x": 0.50, "y": 0.987 },
    { "x": 0.48, "y": 0.982 },
    { "x": 0.46, "y": 0.978 },
    { "x": 0.44, "y": 0.968 },
    { "x": 0.42, "y": 0.958 },
    { "x": 0.40, "y": 0.942 },
    { "x": 0.38, "y": 0.920 },
    { "x": 0.36, "y": 0.885 },
    { "x": 0.34, "y": 0.845 },
    { "x": 0.32, "y": 0.780 },
    { "x": 0.31, "y": 0.700 },
    { "x": 0.31, "y": 0.650 },
    { "x": 0.32, "y": 0.580 },
    { "x": 0.34, "y": 0.525 },
    { "x": 0.37, "y": 0.500 },
]

soundNames = ["alarm", "blip", "step"]

sounds = {}

for soundName in soundNames:
    sounds[soundName] = pyglet.media.load("assets/audio/" + soundName + ".wav", streaming=False)

for i in range(starCount):
    stars.append({
        "x": random.random(),
        "y": random.random()
    })

@window.event
def on_draw():
    global gameState
    if gameState == "running":
        drawGame()
    elif gameState == "intro":
        drawIntro()

timeSinceAudioPlayed = 0
dotsShown = 0

def drawIntro():
    global gameState, introElapsed, timeSinceAudioPlayed, dotsShown
    
    window.clear()

    if introElapsed < 10:
        label = pyglet.text.Label(str(math.ceil(5 - introElapsed / 2)),
            font_name = "Poppins",
            font_size = 200,
            x = window.width / 2,
            y = window.height / 2,
            color = (255, 255, 255, round((((2 - introElapsed) / 2) % 2) * 255)),
            anchor_x = "center", anchor_y = "center")
            
        label.draw()
    elif introElapsed <= 10.5:
        pass
    elif introElapsed > 10.5 and introElapsed < 12.5:
        drawConsole()

        cover = shapes.Rectangle(
            x = 0,
            y = 0,
            width = window.width,
            height = window.height,
            color = ( 0, 0, 0 )
        )
        cover.opacity = (2 - (introElapsed - 10.5)) * (255 / 2)
        cover.draw()
    elif introElapsed < 20.5:
        drawConsole()
        if dotsShown < len(shipPath):
            if timeSinceAudioPlayed > 1 - ((introElapsed - 12.5) / 5):
                sounds["blip"].play()
                timeSinceAudioPlayed = 0
                dotsShown += 1
        else:
            if timeSinceAudioPlayed > 0.5:
                sounds["alarm"].play()
                timeSinceAudioPlayed = 0
        if introElapsed >= 18.5:
            cover = shapes.Rectangle(
                x = 0,
                y = 0,
                width = window.width,
                height = window.height,
                color = ( 0, 0, 0 )
            )
            cover.opacity = (introElapsed - 16.5) * (255 / 2)
            cover.draw()
    else:
        gameState = "running"

        
    label = pyglet.text.Label("Space to skip",
        font_name = "Poppins",
        font_size = 20,
        x = window.width / 2,
        y = 0,
        color = (255, 255, 255, 100),
        anchor_x = "center", anchor_y = "bottom")
        
    label.draw()

def drawConsole():
    global dotsShown

    consoleback = shapes.Rectangle(
        x = 15,
        y = 15,
        width = window.width - 30,
        height = window.height - 30,
        color = ( 20, 20, 40 )
    )
    consoleback.draw()

    consolescreen = shapes.Rectangle(
        x = 30,
        y = 30,
        width = window.width - 60,
        height = window.height - 60,
        color = ( 0, 0, 0 )
    )
    consolescreen.draw()

    for star in stars:
        planet = shapes.Circle(
            x = star["x"] * (window.width - 100) + 50,
            y = star["y"] * (window.height - 100) + 50,
            radius = 5,
            color = ( 200, 200, 200 )
        )
        planet.draw()
    
    ship = shapes.Circle(
        x = window.width / 4 * 3,
        y = window.height / 4 * 3,
        radius = 20,
        color = ( 40, 40, 100 )
    )
    ship.draw()

    index = 0
    for point in shipPath:
        index += 1
        if(index > dotsShown):
            continue
        
        pathPointColor = ( 150, 255, 150 )
        if dotsShown == len(shipPath):
            pathPointColor = ( 255, 150, 150 )
        shipPathPoint = shapes.Circle(
            x = point["x"] * (window.width - 100) + 50,
            y = point["y"] * (window.height - 100) + 50,
            radius = 5,
            color = pathPointColor
        )
        shipPathPoint.draw()
        
    planet = shapes.Circle(
        x = window.width / 2,
        y = window.height / 2,
        radius = 200,
        color = ( 100, 40, 40 )
    )
    planet.draw()

def drawGame():
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
    global gameState

    if gameState == "running":
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
    elif gameState == "intro":
        if symbol == key.SPACE:
            gameState = "running"

@window.event
def on_key_release(symbol, modifiers):
    if gameState == "running":
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
    global introElapsed, timeSinceAudioPlayed
    
    if gameState == "running":
        updateGame(dt)
    elif gameState == "intro":
        introElapsed += 1 / framerate
        timeSinceAudioPlayed += 1 / framerate

def updateGame(dt):
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