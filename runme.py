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

backpackSlots = 4
inventoryItems = [ { "item": "pickaxe", "quantity": 1 }, { "item": 0, "quantity": 1 } ]

selectedHand = 1

for _ in range(backpackSlots):
    inventoryItems.append({ "item": 0, "quantity": 1 })

itemTypes = {
    "pickaxe": {
        "path": "pickaxe.png",
        "name": "Pickaxe",
        "canMine": True
    },
    "ironChunks": {
        "path": "ironChunks.png",
        "name": "Iron Chunks",
        "canMine": False
    },
    "carbonChunks": {
        "path": "carbonChunks.png",
        "name": "Carbon Chunks",
        "canMine": False
    },
    "drill": {
        "path": "drill.png",
        "name": "Drill",
        "canMine": False
    }
}

for itemType in itemTypes:
    itemTypes[itemType]["image"] = pyglet.image.load("assets/images/items/" + itemTypes[itemType]["path"])

fabricationRecipes = [
    {
        "inputs": [
            { "item": "ironChunks", "quantity": 6 }
        ],
        "output": { "item": "smelter", "quantity": 1 }
    },
    {
        "inputs": [
            { "item": "ironChunks", "quantity": 1 },
            { "item": "carbonChunks", "quantity": 1 }
        ],
        "output": { "item": "drill", "quantity": 1 }
    }
]

gameState = "intro"
introElapsed = 0

pyglet.font.add_file("assets/fonts/PressStart2P-Regular.ttf")
pyglet.font.load("Press Start 2P")

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

UIImageFiles = ["backpackOpen", "backpackClosed"]
UIImages = {}

for UIImage in UIImageFiles:
    UIImages[UIImage] = pyglet.image.load("assets/images/UI/" + UIImage + ".png")

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

structuresGenerated = {}

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
        "isOre": True,
        "animated": False,
        "gives": [
            {"item": "ironChunks", "min": 1, "max": 3}
        ]
    },
    "carbonOre": {
        "path": "carbonOre.png",
        "breakTime": 2,
        "isOre": True,
        "animated": False,
        "gives": [
            {"item": "carbonChunks", "min": 2, "max": 5}
        ]
    },
    "drill": {
        "path": "drill.png",
        "breakTime": 3,
        "isOre": False,
        "animated": True,
        "columns": 14
    }
}

for chunkStructure in chunkStructures:
    if chunkStructures[chunkStructure]["animated"]:
        chunkStructures[chunkStructure]["image"] = pyglet.image.ImageGrid(
            pyglet.image.load("assets/images/structures/" + chunkStructures[chunkStructure]["path"]),
            1, chunkStructures[chunkStructure]["columns"]
        )
    else:
        chunkStructures[chunkStructure]["image"] = pyglet.image.load("assets/images/structures/" + chunkStructures[chunkStructure]["path"])

UIHintFiles = {
    "ToMine": "ToMine.png",
    "ToBreak": "ToBreak.png"
}

UIHints = {}

for UIHintFile in UIHintFiles:
    UIHints[UIHintFile] = pyglet.image.load("assets/images/UI/" + UIHintFiles[UIHintFile])

LMBHeld = False
BreakTime = 0

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
            font_name = "Press Start 2P",
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
        font_name = "Press Start 2P",
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

LMBClicked = False

def drawGame():
    global walkingFrame, oxygen, oldX, oldY, BreakTime, LMBClicked

    window.clear()
    
    # Make sure the world is centered around the player, not the bottom left of the screen
    calculatedX = x - window.width / 2
    calculatedY = y + window.height / 2

    playerTileX = math.floor(calculatedX / tileSize)
    playerTileY = math.floor(calculatedY / tileSize)

    # Generate new chunks if we moved
    if not playerTileX == oldX:
        oldX = playerTileX
        checkAndGenerateStructures(calculatedX, calculatedY, playerTileX, playerTileY)

    if not playerTileY == oldY:
        oldY = playerTileY
        checkAndGenerateStructures(calculatedX, calculatedY, playerTileX, playerTileY)

    offsetX = round(-calculatedX % tileSize)
    offsetY = round(calculatedY % tileSize / 1.5)

    batch = pyglet.graphics.Batch()
    ground = pyglet.graphics.OrderedGroup(0)
    ground2 = pyglet.graphics.OrderedGroup(1)
    ground3 = pyglet.graphics.OrderedGroup(2)
    structures = pyglet.graphics.OrderedGroup(3)

    sprites = []

    miningOres = False

    if inventoryItems[selectedHand - 1]["item"] in itemTypes:
        if itemTypes[inventoryItems[selectedHand - 1]["item"]]["canMine"] == True:
            miningOres = True

    closestOre = 100000
    closestOreData = {
        "x": 0,
        "y": 0,
        "screenX": 0,
        "screenY": 0,
        "data": 0
    }

    closestTileMouse = 100000
    
    # # Draw ground tiles
    for tileX in range(-3, round(window.width / tileSize * 2) + 1):
        for tileY in range(-2, round(window.height / tileSize * 1.5) + 1):
            tileWorldX = tileX / 2 + math.ceil(calculatedX / tileSize)
            tileWorldY = tileY - math.ceil(calculatedY / tileSize)

            selectedImage = tiles["mars"]
            if noise([tileWorldX / 4, tileWorldY / 4]) > 0:
                selectedImage = tiles["marsLight"]

            groundGroup = ground
            
            if (tileWorldX % 2 == 0 and not tileWorldY % 2 == 0):
                groundGroup = ground2
            if (tileWorldX % 2 == 0 and tileWorldY % 2 == 0):
                groundGroup = ground3
            
            sprite = pyglet.sprite.Sprite(img = selectedImage, batch = batch, group = groundGroup)
            sprite.x = tileX * tileSize / 2 + offsetX
            if tileX % 2 == 0:
                sprite.y = tileY * tileSize / 1.5 + offsetY
            else:
                sprite.y = tileY * tileSize / 1.5 + tileSize / 1.5 / 2 + offsetY
            sprite.scale = tileSize / 1024

            sprites.append(sprite)

            tileStructureCode = str(tileWorldX) + "_" + str(tileWorldY)

            if tileStructureCode in structuresGenerated:
                chunkStrucutre = structuresGenerated[tileStructureCode]
                
                if chunkStrucutre in chunkStructures:
                    structureData = chunkStructures[chunkStrucutre]

                    chunkStructureImage = None
                    if structureData["animated"]:
                        chunkStructureImage = structureData["image"][globalAnimationFrame % structureData["columns"]]
                    else:
                        chunkStructureImage = structureData["image"]

                    sprite = pyglet.sprite.Sprite(img = chunkStructureImage, batch = batch, group = structures)
                    structureX = tileX * tileSize / 2 + offsetX
                    structureY = 0
                    if tileX % 2 == 0:
                        structureY = tileY * tileSize / 1.5 + offsetY
                    else:
                        structureY = tileY * tileSize / 1.5 + tileSize / 1.5 / 2 + offsetY

                    if miningOres == True:
                        distanceToOre = distance(structureX + tileSize / 2, structureY + tileSize / 2, window.width / 2, window.height / 2)
                        if distanceToOre < closestOre:
                            closestOre = distanceToOre
                            closestOreData["x"] = tileWorldX
                            closestOreData["y"] = tileWorldY

                            closestOreData["screenX"] = structureX
                            closestOreData["screenY"] = structureY

                            closestOreData["data"] = structureData

                    sprite.x = structureX
                    sprite.y = structureY

                    sprite.scale = tileSize / 2048

                    sprites.append(sprite)

    batch.draw()

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

    # Triangle
    # pyglet.graphics.draw_indexed(3, pyglet.gl.GL_TRIANGLES,
    #     [0, 1, 2],
    #     ('v2i', (100, 100,
    #             150, 100,
    #             150, 150)),
    #     ('c3B', (100, 100, 100, 100, 100, 100, 100, 100, 100))
    # )
    # pyglet.graphics.draw_indexed(3, pyglet.gl.GL_TRIANGLES,
    #     [0, 1, 2],
    #     ('v2i', (106, 102,
    #             148, 102,
    #             148, 144)),
    #     ('c3B', (255, 100, 100, 255, 0, 0, 255, 100, 100))
    # )

    rocketDirectionColor = ( 150, 150, 150 )
    if(globalAnimationFrame % 6 >= 3):
        rocketDirectionColor = ( 255, 100, 100 )
    
    rocketDirectionVector = {
        "x": staticAssetList[0]["x"] - calculatedX,
        "y": staticAssetList[0]["y"] - calculatedY
    }

    normalizedRocketDirectionVector = rocketDirectionVector

    rocketDirectionVectorMagnitude = math.sqrt(-rocketDirectionVector["x"] * -rocketDirectionVector["x"] + -rocketDirectionVector["y"] * -rocketDirectionVector["y"])

    normalizedRocketDirectionVector["x"] = normalizedRocketDirectionVector["x"] / rocketDirectionVectorMagnitude
    normalizedRocketDirectionVector["y"] = normalizedRocketDirectionVector["y"] / rocketDirectionVectorMagnitude

    towardsRocket = shapes.Rectangle(
        x = window.width / 2 + (normalizedRocketDirectionVector["x"] * 200),
        y = window.height / 2 - (normalizedRocketDirectionVector["y"] * 200),
        width = 20,
        height = 20,
        color = rocketDirectionColor
    )
    towardsRocket.draw()
    
    
    if closestOre != 100000:
        if closestOre < 300:
            hintX = closestOreData["screenX"] + tileSize / 4
            hintY = closestOreData["screenY"] + tileSize / 2

            ShowUIHint(hintX, hintY, "ToMine")

            bar = shapes.Rectangle(
                x = hintX - 250,
                y = hintY - 250,
                width = 500,
                height = 50,
                color = ( 100, 100, 100 )
            )
            bar.opacity = 150
            bar.draw()

            filled = shapes.Rectangle(
                x = hintX - 245,
                y = hintY - 245,
                width = 490 * (BreakTime / closestOreData["data"]["breakTime"]),
                height = 40,
                color = ( 25, 100, 25 )
            )
            filled.opacity = 150
            filled.draw()
        else:
            BreakTime = 0
    else:
        BreakTime = 0

    if closestOreData["data"] == 0:
        closestOreData["data"] = {
            "breakTime": 1
        }

    if BreakTime >= closestOreData["data"]["breakTime"]:
        structuresGenerated[str(closestOreData["x"]) + "_" + str(closestOreData["y"])] = 0
        for give in closestOreData["data"]["gives"]:
            amount = random.randint(give["min"], give["max"])
            giveItem(give["item"], amount)
        BreakTime = 0

    LMBClicked = False

def giveItem(item, amount):
    global inventoryItems

    if item in itemTypes:
        for inventorySlot in inventoryItems:
            if inventorySlot["item"] == 0:
                inventorySlot["item"] = item
                inventorySlot["quantity"] = amount
                break
            elif inventorySlot["item"] == item:
                inventorySlot["quantity"] += amount
                break

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))

def ShowUIHint(x, y, UIHint):
    if UIHint in UIHints:
        UIHintImage = UIHints[UIHint]
        sprite = pyglet.sprite.Sprite(img = UIHintImage)
        sprite.x = x - 250
        sprite.y = y - 200

        sprite.scale = 500 / 2176

        sprite.draw()

def checkAndGenerateStructures(calculatedX, calculatedY, structureX, structureY):
    for structureX in range(-3, round(window.width / tileSize * 2) + 1):
        for structureY in range(-2, round(window.height / tileSize * 1.5) + 1):
            structureWorldX = structureX + math.floor(calculatedX * 2 / tileSize)
            structureWorldY = structureY - math.floor(calculatedY / tileSize)
            structureCode = str(structureWorldX / 2) + "_" + str(structureWorldY)
            if not structureCode in structuresGenerated:
                structuresGenerated[structureCode] = generateStructure(structureWorldX, structureWorldY)

# TODO: Make this psudorandom depending on a seed rather than 100% random
def generateStructure(structureX, structureY):
    if random.random() > 0.98:
        chunkStructure = random.choice(["carbonOre", "ironOre"])
        return chunkStructure
    else:
        return 0

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
            font_name = "Press Start 2P",
            font_size = 25,
            x = window.width - 495,
            y = window.height - 15 - (55 * (index - 1)),
            color = (255, 255, 255, 255),
            anchor_x = "left", anchor_y = "top")
        label.draw()

        if UIBar["countdown"]:
            countdownTime = "{:0>2d}".format(math.floor(UIBar["countdownTime"] / 60)) + ":" + "{:0>2d}".format(math.floor(UIBar["countdownTime"]) % 60)
            countdown = pyglet.text.Label(countdownTime,
                font_name = "Press Start 2P",
                font_size = 25,
                x = window.width - 10,
                y = window.height - 15 - (55 * (index - 1)),
                color = (255, 255, 255, 255),
                anchor_x = "right", anchor_y = "top")
            countdown.draw()
    
    drawInventory()


keysPressed = {
    "left": False,
    "right": False,
    "up": False,
    "down": False,
    "w": False,
    "a": False,
    "s": False,
    "d": False
}

@window.event
def on_key_press(symbol, modifiers):
    global gameState, backpackOpened, selectedHand

    if gameState == "running":
        if symbol == key.LEFT:
            keysPressed["left"] = True
        elif symbol == key.RIGHT:
            keysPressed["right"] = True
        elif symbol == key.UP:
            keysPressed["up"] = True
        elif symbol == key.DOWN:
            keysPressed["down"] = True
        elif symbol == key.B:
            backpackOpened = not backpackOpened
        elif symbol == 49: # numbers 1 through 6
            selectedHand = 1
        elif symbol == 50:
            selectedHand = 2
        elif symbol == 51:
            swapWithSelectedHand(3)
        elif symbol == 52:
            swapWithSelectedHand(4)
        elif symbol == 53:
            swapWithSelectedHand(5)
        elif symbol == 54:
            swapWithSelectedHand(6)
        elif symbol == key.W:
            keysPressed["w"] = True
        elif symbol == key.A:
            keysPressed["a"] = True
        elif symbol == key.S:
            keysPressed["s"] = True
        elif symbol == key.D:
            keysPressed["d"] = True
    elif gameState == "intro":
        if symbol == key.SPACE:
            gameState = "running"

def swapWithSelectedHand(swapWith):
    global inventoryItems

    temp = inventoryItems[swapWith - 1]
    inventoryItems[swapWith - 1] = inventoryItems[selectedHand - 1]
    inventoryItems[selectedHand - 1] = temp

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
        elif symbol == key.W:
            keysPressed["w"] = False
        elif symbol == key.A:
            keysPressed["a"] = False
        elif symbol == key.S:
            keysPressed["s"] = False
        elif symbol == key.D:
            keysPressed["d"] = False

from pyglet.window import mouse

@window.event
def on_mouse_press(x, y, button, modifiers):
    global LMBHeld, LMBClicked

    if gameState == "running":
        if button == mouse.LEFT:
            LMBHeld = True
            LMBClicked = True

@window.event
def on_mouse_release(x, y, button, modifiers):
    global LMBHeld, BreakTime
    
    if gameState == "running":
        if button == mouse.LEFT:
            LMBHeld = False
            BreakTime = 0

mouseX = 0
mouseY = 0

@window.event
def on_mouse_motion(x, y, movementX, movementY):
    global mouseX, mouseY

    mouseX = x
    mouseY = y

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
    global x, y, xMomentum, yMomentum, oxygen, BreakTime

    movementSpeed = 60 * dt

    oxygenDepletionRate = oxygenDepletePerSecond * ((math.sqrt(xMomentum * xMomentum + yMomentum * yMomentum) + 25) / 25)

    oxygen -= oxygenDepletionRate * dt

    if keysPressed["left"] or keysPressed["a"]:
        xMomentum -= movementSpeed
    if keysPressed["right"] or keysPressed["d"]:
        xMomentum += movementSpeed
    if keysPressed["up"] or keysPressed["w"]:
        yMomentum -= movementSpeed
    if keysPressed["down"] or keysPressed["s"]:
        yMomentum += movementSpeed

    x += xMomentum
    y += yMomentum

    xMomentum /= 1.05
    yMomentum /= 1.05

    if math.fabs(xMomentum) < 0.5:
        xMomentum = 0
    if math.fabs(yMomentum) < 0.5:
        yMomentum = 0

    if LMBHeld == True:
        BreakTime += 1 * dt

slotSize = 85
backpackOpened = False

fabricatingMenuSelected = 0

def drawInventory():
    global backpackOpened

    backpackColor = ( 100, 100, 100 )
    if backpackOpened == True:
        backpackColor = ( 80, 80, 80 )
    
    backpackIcon = shapes.Rectangle(
        x = 5,
        y = 5,
        width = slotSize,
        height = slotSize,
        color = backpackColor
    )
    if mouseX > 5 and mouseY > 5 and mouseX < 5 + slotSize and mouseY < 5 + slotSize:
        backpackIcon.opacity = 255
        if LMBClicked:
            backpackOpened = not backpackOpened
    else:
        backpackIcon.opacity = 200
    backpackIcon.draw()

    backpackState = "backpackClosed"
    if backpackOpened == True:
        backpackState = "backpackOpen"
    
    backpackImage = pyglet.sprite.Sprite(img = UIImages[backpackState])
    backpackImage.x = 5
    backpackImage.y = 5

    backpackImage.scale = slotSize / 512
    backpackImage.draw()

    backpackLabel = pyglet.text.Label("B",
        font_name = "Press Start 2P",
        font_size = 15,
        x = 10,
        y = slotSize,
        color = (255, 255, 255, 255),
        anchor_x = "left", anchor_y = "top")
    backpackLabel.draw()
    
    slotOneColor = (100, 100, 100)
    if selectedHand == 1:
        slotOneColor = (150, 150, 150)
    drawSlot(slotSize + 10, 5, slotOneColor, inventoryItems[0], "1")

    slotTwoColor = (100, 100, 100)
    if selectedHand == 2:
        slotTwoColor = (150, 150, 150)
    drawSlot(slotSize * 2 + 15, 5, slotTwoColor, inventoryItems[1], "2")

    if backpackOpened == True:
        for backpackSlot in range(backpackSlots):
            drawSlot(5, (slotSize + 5) * (1 + backpackSlot) + 5, (80, 80, 80), inventoryItems[2 + backpackSlot], str(backpackSlot + 3))

        fabricatingMenu = shapes.Rectangle(
            x = (slotSize + 10), 
            y = (slotSize + 10),
            width = (slotSize + 5) * 6 - 5,
            height = (slotSize + 5) * 4 - 5,
            color = ( 80, 80, 80 )
        )
        fabricatingMenu.opacity = 200
        fabricatingMenu.draw()
        
        labelBackground = shapes.Rectangle(
            x = (slotSize + 10), 
            y = (slotSize + 5) * 5,
            width = 230,
            height = 25,
            color = ( 80, 80, 80 )
        )
        labelBackground.opacity = 200
        labelBackground.draw()

        fabricationLabel = pyglet.text.Label("Fabrication",
            font_name = "Press Start 2P",
            font_size = 15,
            x = (slotSize + 10) + 5,
            y = (slotSize + 5) * 5 + 20,
            color = (255, 255, 255, 255),
            anchor_x = "left", anchor_y = "top")
        fabricationLabel.draw()

        index = 0
        for fabricationRecipe in fabricationRecipes:
            drawSlot(slotSize + 15 + ((slotSize + 5) * index), (slotSize + 5) * 4, ( 100, 100, 100 ), fabricationRecipe["output"], "", selectFabricationRecipe, fabricationRecipe)
            index += 1

        if not fabricatingMenuSelected == 0:
            index = 0
            canFabricate = True
            for fabricationInput in fabricatingMenuSelected["inputs"]:
                hasMaterialsColor = ( 150, 80, 80 )
                if playerHasMaterials(fabricationInput) == True:
                    hasMaterialsColor = ( 80, 150, 80 )
                else:
                    canFabricate = False
                drawSlot(slotSize + 15 + ((slotSize + 5) * index), (slotSize + 5) * 3 - 10, hasMaterialsColor, fabricationInput, "")
                index += 1

            if mouseX > slotSize + 15 and mouseX < slotSize + 15 + (slotSize + 5) * 6 - 15 and mouseY > (slotSize + 5) + 10 and mouseY < (slotSize + 5) + 10 + 30:
                if canFabricate == True:
                    fabricateButtonColor = ( 120, 170, 120 )
                else:
                    fabricateButtonColor = ( 170, 120, 120 )
                
                if LMBClicked:
                    if canFabricate == True:
                        for fabricationInput in fabricatingMenuSelected["inputs"]:
                            item = fabricationInput["item"]
                            quantity = fabricationInput["quantity"]

                            removeItem(item, quantity)
                        giveItem(fabricatingMenuSelected["output"]["item"], fabricatingMenuSelected["output"]["quantity"])
            else:
                if canFabricate == True:
                    fabricateButtonColor = ( 100, 150, 100 )
                else:
                    fabricateButtonColor = ( 150, 100, 100 )

            fabricateButtonRectangle = shapes.Rectangle(
                x = slotSize + 15, 
                y = (slotSize + 5) + 10,
                width = (slotSize + 5) * 6 - 15,
                height = 30,
                color = fabricateButtonColor
            )
            fabricateButtonRectangle.draw()

            fabricateButtonLabel = pyglet.text.Label("Fabricate",
                font_name = "Press Start 2P",
                font_size = 15,
                x = (slotSize + 5) * 4 + 10,
                y = (slotSize + 5) + 5,
                color = (255, 255, 255, 255),
                anchor_x = "center", anchor_y = "bottom")
            fabricateButtonLabel.draw()

def removeItem(item, quantity):
    quantityLeft = quantity
    for slotItem in inventoryItems:
        if slotItem["item"] == item:
            if slotItem["quantity"] > quantityLeft:
                slotItem["quantity"] -= quantityLeft
                quantityLeft = 0
                break
            else:
                quantityLeft -= slotItem["quantity"]
                slotItem["quantity"] = 1
                slotItem["item"] = 0
                

def playerHasMaterials(materials):
    playerItems = {}
    for slotContent in inventoryItems:
        item = slotContent["item"]
        quantity = slotContent["quantity"]

        if item in playerItems:
            playerItems[item] += quantity
        else:
            playerItems[item] = quantity

    if materials["item"] in playerItems:
        if playerItems[materials["item"]] >= materials["quantity"]:
            return True

    return False

def selectFabricationRecipe(recipe):
    global fabricatingMenuSelected

    fabricatingMenuSelected = recipe

def drawSlot(slotX, slotY, color, item, label, clickCallback = None, callbackParameters = None):
    slotSquare = shapes.Rectangle(
        x = slotX, 
        y = slotY,
        width = slotSize,
        height = slotSize,
        color = color
    )
    if mouseX > slotX and mouseY > slotY and mouseX < slotX + slotSize and mouseY < slotY + slotSize:
        slotSquare.opacity = 255
        if LMBClicked == True:
            if not clickCallback == None:
                if callbackParameters == None:
                    clickCallback()
                else:
                    clickCallback(callbackParameters)
    else:
        slotSquare.opacity = 200
    slotSquare.draw()

    if item["item"] in itemTypes:
        itemData = itemTypes[item["item"]]

        itemImage = pyglet.sprite.Sprite(img = itemData["image"])
        itemImage.x = slotX
        itemImage.y = slotY

        itemImage.scale = slotSize / 1024
        itemImage.draw()
        
    slotLabel = pyglet.text.Label(label,
        font_name = "Press Start 2P",
        font_size = 15,
        x = slotX + 5,
        y = slotY + slotSize - 5,
        color = (255, 255, 255, 255),
        anchor_x = "left", anchor_y = "top")
    slotLabel.draw()

    amount = item["quantity"]
    if amount > 1:
        slotAmount = pyglet.text.Label(str(amount),
            font_name = "Press Start 2P",
            font_size = 15,
            x = slotX + slotSize - 5,
            y = slotY - 5,
            color = (255, 255, 255, 255),
            anchor_x = "right", anchor_y = "bottom")
        slotAmount.draw()

pyglet.clock.schedule_interval(update, 1 / framerate)

pyglet.app.run()