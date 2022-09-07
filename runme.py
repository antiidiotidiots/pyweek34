import chunk
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

chunkSize = 8 # In tiles

chunkSizeX = chunkSize * 2
chunkSizeY = chunkSize

walkingFrame = 0

staticAssets = [
    {
        "animated": False,
        "path": "rocket.png",
        "x": 0,
        "y": 0,
        "scale": tileSize
    },
    {
        "animated": True,
        "path": "fire.png",
        "x": 75,
        "y": 300,
        "columns": 3,
        "scale": tileSize
    },
    {
        "animated": True,
        "path": "fire.png",
        "x": 350,
        "y": 200,
        "columns": 3,
        "scale": tileSize
    }
]

staticAssetList = []

for staticAsset in staticAssets:
    if staticAsset["animated"]:
        staticAssetList.append({
            "animated": True,
            "image": pyglet.image.ImageGrid(
                pyglet.image.load("assets/images/static/" + staticAsset["path"]),
                1, staticAsset["columns"]),
            "x": staticAsset["x"],
            "y": staticAsset["y"],
            "scale": staticAsset["scale"] / 1024,
            "frames": staticAsset["columns"]
        })
    else:
        staticAssetList.append({
            "animated": False,
            "image": pyglet.image.load("assets/images/static/" + staticAsset["path"]),
            "x": staticAsset["x"],
            "y": staticAsset["y"],
            "scale": staticAsset["scale"] / 1024
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

chunksGenerated = {}

soundNames = ["alarm", "blip", "step"]

sounds = {}

for soundName in soundNames:
    sounds[soundName] = pyglet.media.load("assets/audio/" + soundName + ".wav", streaming=False)

for i in range(starCount):
    stars.append({
        "x": random.random(),
        "y": random.random()
    })

chunkStructures = {
    "ironOre": {
        "path": "ironOre.png",
        "breakTime": 3,
        "gives": [
            {"type": "ironChunk", "min": "1", "max": "3"}
        ]
    },
    "carbonOre": {
        "path": "carbonOre.png",
        "breakTime": 2,
        "gives": [
            {"type": "carbonChunk", "min": "2", "max": "5"}
        ]
    }
}

for chunkStructure in chunkStructures:
    chunkStructures[chunkStructure]["image"] = pyglet.image.load("assets/images/structures/" + chunkStructures[chunkStructure]["path"])

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

oldX = 0
oldY = 0

def drawGame():
    global walkingFrame, oxygen, oldX, oldY

    window.clear()
    
    # Make sure the world is centered around the player, not the bottom left of the screen
    calculatedX = x - window.width / 2
    calculatedY = y + window.height / 2
    
    chunkX = math.floor(calculatedX / (chunkSize * tileSize))
    chunkY = math.floor(calculatedY / (chunkSize * tileSize))
    chunkCode = str(chunkX) + "-" + str(chunkY)

    # Generate new chunks if we moved
    if not calculatedX == oldX:
        oldX = calculatedX
        checkAndGenerateChunks(calculatedX, calculatedY, chunkX, chunkY, chunkCode)

    if not calculatedY == oldY:
        oldY = calculatedY
        checkAndGenerateChunks(calculatedX, calculatedY, chunkX, chunkY, chunkCode)

    offsetX = round(-calculatedX % tileSize)
    offsetY = round(calculatedY % tileSize / 1.5)
    
    # Draw ground tiles
    for tileX in range(-3, round(window.width / tileSize * 2) + 1):
        for tileY in range(-2, round(window.height / tileSize * 1.5) + 1):
            tileWorldX = tileX / 2 + math.ceil(calculatedX / tileSize)
            tileWorldY = tileY - math.ceil(calculatedY / tileSize)

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

    # Draw chunk structures like ores
    if chunkCode in chunksGenerated:
        for structureX in range(chunkSizeX):
            for structureY in range(chunkSizeY):
                chunkStructureWorldX = round(structureX / 2 + math.ceil(calculatedX / tileSize))
                chunkStructureWorldY = round(structureY - math.ceil(calculatedY / tileSize))

                if(chunkStructureWorldX < 0 or chunkStructureWorldX >= len(chunksGenerated[chunkCode])):
                    continue
                if(chunkStructureWorldY < 0 or chunkStructureWorldY >= len(chunksGenerated[chunkCode][chunkStructureWorldX])):
                    continue

                chunkStructure = chunksGenerated[chunkCode][chunkStructureWorldX][chunkStructureWorldY]

                if not chunkStructure == 0:
                    chunkStructureData = chunkStructures[chunkStructure]

                    sprite = pyglet.sprite.Sprite(img = chunkStructureData["image"])
                    sprite.x = structureX * tileSize / 2 + offsetX
                    if tileX % 2 == 0:
                        sprite.y = structureY * tileSize / 1.5 + offsetY
                    else:
                        sprite.y = structureY * tileSize / 1.5 + tileSize / 1.5 / 2 + offsetY
                    sprite.scale = tileSize / 1024

                    sprite.draw() # Draw sprite


    # Draw static stuff like the rocket that are under the player
    for staticAsset in staticAssetList:
        if calculatedY >= staticAsset["y"]:
            drawStaticAsset(staticAsset, calculatedX, calculatedY)

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

    # Draw static stuff like the rocket that are over the player
    for staticAsset in staticAssetList:
        if calculatedY < staticAsset["y"]:
            drawStaticAsset(staticAsset, calculatedX, calculatedY)

    # Draw the oxygen bars, inventory, etc.
    drawUI()

oldChunkX = 0
oldChunkY = 0

def checkAndGenerateChunks(calculatedX, calculatedY, chunkX, chunkY, chunkCode):
    global oldChunkX, oldChunkY

    if (not chunkX == oldChunkX) or (not chunkY == oldChunkY):
        oldChunkX = chunkX
        oldChunkY = chunkY

        if not chunkCode in chunksGenerated:
            chunksGenerated[chunkCode] = generateChunk(chunkX, chunkY)

# TODO: Make this psudorandom rather than 100% random
def generateChunk(chunkX, chunkY):
    result = []

    for tileX in range(chunkSizeX):
        result.append([])
        for tileY in range(chunkSizeY):
            if random.random() > 0.8:
                chunkStructure = random.choice(list(chunkStructures.keys()))
                result[tileX].append(chunkStructure)
            else:
                result[tileX].append(0)

    print(result)

    return result

globalAnimationFrame = 0

def drawStaticAsset(staticAsset, calculatedX, calculatedY):
    global globalAnimationFrame

    if staticAsset["animated"]:
        sprite = pyglet.sprite.Sprite(img = staticAsset["image"][globalAnimationFrame % staticAsset["frames"]])
        sprite.x = staticAsset["x"] - round(calculatedX)
        sprite.y = staticAsset["y"] + round(calculatedY / 1.5)

        sprite.scale = staticAsset["scale"]

        sprite.draw()
    else:
        sprite = pyglet.sprite.Sprite(img = staticAsset["image"])
        sprite.x = staticAsset["x"] - round(calculatedX)
        sprite.y = staticAsset["y"] + round(calculatedY / 1.5)

        sprite.scale = staticAsset["scale"]

        sprite.draw()

def drawUI():
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
            keysPressed["left"] = True
        elif symbol == key.RIGHT:
            keysPressed["right"] = True
        elif symbol == key.UP:
            keysPressed["up"] = True
        elif symbol == key.DOWN:
            keysPressed["down"] = True
    elif gameState == "intro":
        if symbol == key.SPACE:
            gameState = "running"

@window.event
def on_key_release(symbol, modifiers):
    if gameState == "running":
        if symbol == key.LEFT:
            keysPressed["left"] = False
        elif symbol == key.RIGHT:
            keysPressed["right"] = False
        elif symbol == key.UP:
            keysPressed["up"] = False
        elif symbol == key.DOWN:
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

timeSinceAnimationFrame = 0

def update(dt):
    global introElapsed, timeSinceAudioPlayed, timeSinceAnimationFrame, globalAnimationFrame
    
    if gameState == "running":
        updateGame(dt)
        timeSinceAnimationFrame += 1 / framerate
        if timeSinceAnimationFrame > 0.1:
            timeSinceAnimationFrame = 0
            globalAnimationFrame += 1
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