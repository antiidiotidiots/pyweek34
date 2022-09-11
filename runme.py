import pyglet
from perlin_noise import PerlinNoise
import math
from pyglet.window import key

from pyglet import shapes

import random

countdown = False

window = pyglet.window.Window(fullscreen=True, caption="Stranded")

x = 0
y = 0

xMomentum = 0
yMomentum = 0

oxygen = 1

oxygenMinutes = 12
oxygenDepletePerSecond = 1 / (oxygenMinutes * 60)

backpackSlots = 7
inventoryItems = [ { "item": "pickaxe", "quantity": 1 }, { "item": 0, "quantity": 1 } ]

selectedHand = 1

for _ in range(backpackSlots):
    inventoryItems.append({ "item": 0, "quantity": 1 })

itemTypes = {
    "pickaxe": {
        "path": "pickaxe.png",
        "name": "Pickaxe",
        "canMine": True,
        "canBuild": False
    },
    "ironChunks": {
        "path": "ironChunks.png",
        "name": "Iron Chunks",
        "canMine": False,
        "canBuild": False
    },
    "copperChunks": {
        "path": "copperChunks.png",
        "name": "Copper Chunks",
        "canMine": False,
        "canBuild": False
    },
    "carbonChunks": {
        "path": "carbonChunks.png",
        "name": "Carbon Chunks",
        "canMine": False,
        "canBuild": False
    },
    "drill": {
        "path": "drill.png",
        "name": "Drill",
        "canMine": False,
        "canBuild": True
    },
    "smelter": {
        "path": "smelter.png",
        "name": "Smelter",
        "canMine": False,
        "canBuild": True
    },
    "crudeOil": {
        "path": "crudeOil.png",
        "name": "Crude Oil",
        "canMine": False,
        "canBuild": False
    },
    "copperWire": {
        "path": "copperWire.png",
        "name": "Copper Wire",
        "canMine": False,
        "canBuild": False
    },
    "ironBar": {
        "path": "ironBar.png",
        "name": "Iron Bar",
        "canMine": False,
        "canBuild": False
    },
    "copperBar": {
        "path": "copperBar.png",
        "name": "Copper Bar",
        "canMine": False,
        "canBuild": False
    },
    "solidFuel": {
        "path": "solidFuel.png",
        "name": "Solid Fuel",
        "canMine": False,
        "canBuild": False
    },
    "fuel": {
        "path": "fuel.png",
        "name": "Fuel",
        "canMine": False,
        "canBuild": False
    },
    "coilMaker": {
        "path": "coilMaker.png",
        "name": "Coil Maker",
        "canMine": False,
        "canBuild": True
    },
    "oilRefinery": {
        "path": "oilRefinery.png",
        "name": "Oil Refinery",
        "canMine": False,
        "canBuild": True
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
            { "item": "ironChunks", "quantity": 5 },
            { "item": "solidFuel", "quantity": 10 }
        ],
        "output": { "item": "drill", "quantity": 1 }
    },
    {
        "inputs": [
            { "item": "ironBar", "quantity": 10 }
        ],
        "output": { "item": "coilMaker", "quantity": 1 }
    },
    {
        "inputs": [
            { "item": "ironBar", "quantity": 5 },
            { "item": "copperBar", "quantity": 3 },
            { "item": "copperWire", "quantity": 10 }
        ],
        "output": { "item": "oilRefinery", "quantity": 1 }
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

rocketRepairStages = [
    {
        "requires": [
            { "item": "ironBar", "quantity": 3}
        ],
        "tutorialPrompts": [
            {
                "title": "Keys",
                "description": "Use WASD or arrow keys to\nmove. Pressing 1 or 2 selects\nthat hand. Press N to move\non."
            },
            {
                "title": "Keys 2",
                "description": "Pressing B opens your\nbackpack. There you can \nfabricate things and \nsee 7 more slots."
            },
            {
                "title": "Keys 3",
                "description": "Pressing the number in the\ntop left of a slot swaps\nthe item in that slot\nwith the"
            },
            {
                "title": "Keys 3.5",
                "description": "one in your currently\nselected hand."
            },
            {
                "title": "Moving items",
                "description": "Left click on an item to move\nit. Right click on an\nitem to split the stack\nin half."
            },
            {
                "title": "Mine",
                "description": "Pull out your pickaxe and\nmine the ores around you.\n\nNo, this isn't Minecraft."
            },
            {
                "title": "Mine 2",
                "description": "To mine, go up to an ore\nuntil you see the hint below\nit and simply hold left\nclick."
            },
            {
                "title": "Fabricate",
                "description": "Use the ores you mined to\nmake a smelter."
            },
            {
                "title": "Build",
                "description": "To build something, it must\nbe in your currently\nselected hand."
            },
            {
                "title": "Interact",
                "description": "To interact with an object,\nyour currently selected\nitem must not be the\npickaxe."
            },
            {
                "title": "Smelt",
                "description": "Smelt your ores you gathered\nusing the carbon.\nSmelting carbon makes solid\nfuel."
            },
            {
                "title": "Gather everything",
                "description": "To move on to the next repair\nstage of the rocket,\ngather everything shown\nin the top left."
            }
        ]
    },
    {
        "requires": [
            { "item": "ironBar", "quantity": 30 },
            { "item": "copperBar", "quantity": 30}
        ],
        "tutorialPrompts": [
            {
                "title": "Mine FASTER!",
                "description": "Fabricate a drill using iron\nbars and solid fuel to do the\nwork for you.\nDrills can also gather\ncrude oil, which is used later."
            }
        ]
    },
    {
        "requires": [
            { "item": "copperBar", "quantity": 20},
            { "item": "copperWire", "quantity": 20}
        ],
        "tutorialPrompts": [
            {
                "title": "Coil maker",
                "description": "Create a coil maker and input\ncopper bars."
            }
        ]
    },
    {
        "requires": [
            { "item": "solidFuel", "quantity": 30 },
            { "item": "fuel", "quantity": 30 }
        ],
        "tutorialPrompts": [
            {
                "title": "Fuel the rocket",
                "description": "Craft an oil refinery and\ncreatesome fuel.\nYou're almost there!"
            }
        ]
    }
]

tutorialPromptQueue = []

rocketRepairStage = -1

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

UIImageFiles = ["backpackOpen", "backpackClosed", "play"]
UIImages = {}

for UIImage in UIImageFiles:
    UIImages[UIImage] = pyglet.image.load("assets/images/UI/" + UIImage + ".png")

miscImages = {
    "place": {
        "animated": True,
        "path": "place.png",
        "columns": 13
    },
    "noplace": {
        "animated": True,
        "path": "noplace.png",
        "columns": 13
    },
    "break": {
        "animated": True,
        "path": "break.png",
        "columns": 13
    },
    "nobreak": {
        "animated": True,
        "path": "nobreak.png",
        "columns": 13
    },
    "trash": {
        "animated": False,
        "path": "trash.png"
    }
}

for miscImage in miscImages:
    if miscImages[miscImage]["animated"]:
        miscImages[miscImage]["image"] = pyglet.image.ImageGrid(
            pyglet.image.load("assets/images/misc/" + miscImages[miscImage]["path"]),
            1, miscImages[miscImage]["columns"]
        )
    else:
        miscImages[miscImage]["image"] = pyglet.image.load("assets/images/misc/" + miscImages[miscImage]["path"])

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
        "x": 200,
        "y": 250,
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
    "copperOre": {
        "path": "copperOre.png",
        "breakTime": 3,
        "isOre": True,
        "animated": False,
        "gives": [
            {"item": "copperChunks", "min": 1, "max": 3}
        ]
    },
    "drill": {
        "path": "drill.png",
        "breakTime": 3,
        "isOre": False,
        "animated": True,
        "columns": 14
    },
    "smelter": {
        "path": "smelter.png",
        "breakTime": 4,
        "isOre": False,
        "animated": False,
    },
    "coilMaker": {
        "path": "coilMaker.png",
        "breakTime": 4,
        "isOre": False,
        "animated": False,
    },
    "oilRefinery": {
        "path": "oilRefinery.png",
        "breakTime": 3,
        "isOre": False,
        "animated": False,
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
    "ToBreak": "ToBreak.png",
    "ToInteract": "ToInteract.png"
}

UIHints = {}

for UIHintFile in UIHintFiles:
    UIHints[UIHintFile] = pyglet.image.load("assets/images/UI/" + UIHintFiles[UIHintFile])

LMBHeld = False
RMBHeld = False
BreakTime = 0

@window.event
def on_draw():
    global gameState
    if gameState == "running":
        drawGame()
    elif gameState == "intro":
        drawIntro()
    elif gameState == "ending":
        if endElapsed < 2:
            drawGame()
        
        drawEndScreen()
    elif gameState == "dead":
        if endElapsed < 2:
            drawGame()
        
        drawDeadScreen()

timeSinceAudioPlayed = 0
dotsShown = 0

def drawIntro():
    global gameState, introElapsed, timeSinceAudioPlayed, dotsShown
    
    window.clear()

    if introElapsed < 10:
        if not countdown:
            introElapsed = 10
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
            cover.opacity = math.floor((introElapsed - 16.5) * (255 / 2))
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

def drawDeadScreen():
    endMessage = [
        "Unfortunately, you ran out of oxygen.",
        "",
        "",
        "Thank you so much for playing our game.",
        "Feel free to retry by quitting the game",
        "and restarting.",
        "",
        "Press ESC to close this window."
    ]

    if endElapsed > 2:
        index = 0
        for message in endMessage:
            if endElapsed > 4 + index * 0.6:
                label = pyglet.text.Label(message,
                        font_name = "Press Start 2P",
                        font_size = 20,
                        x = window.width / 2,
                        y = window.height - 30 - (30 * index),
                        color = (255, 255, 255, round(max(((endElapsed - (4 + index * 0.6))) / 2 * 255, 0))),
                        anchor_x = "center", anchor_y = "top")
                        
                label.draw()

            index += 1
    else:
        cover = shapes.Rectangle(
            x = 0,
            y = 0,
            width = window.width,
            height = window.height,
            color = ( 0, 0, 0 )
        )
        cover.opacity = endElapsed * (255 / 2)
        cover.draw()

oldX = 0
oldY = 0

LMBClicked = False
RMBClicked = False
LMBReleased = False
RMBReleased = False
EPressed = False

OpenGUIMenu = 0

def drawGame():
    global walkingFrame, oxygen, oldX, oldY, BreakTime, LMBClicked, RMBClicked, LMBReleased, RMBReleased, EPressed, OpenGUIMenu

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
    structures2 = pyglet.graphics.OrderedGroup(4)
    structures3 = pyglet.graphics.OrderedGroup(5)

    sprites = []

    miningOres = False

    if inventoryItems[selectedHand - 1]["item"] in itemTypes:
        if itemTypes[inventoryItems[selectedHand - 1]["item"]]["canMine"] == True:
            miningOres = True

    closestInteractable = 100000
    closestInteractableData = {
        "x": 0,
        "y": 0,
        "screenX": 0,
        "screenY": 0,
        "data": 0
    }

    closestTileMouse = 100000
    closestTileMouseData = {
        "worldX": 0,
        "worldY": 0,
        "screenX": 0,
        "sceenY": 0
    }
    
    # # Draw ground tiles
    for tileX in range(-3, round(window.width / tileSize * 2) + 1):
        for tileY in list(reversed(range(-2, round(window.height / tileSize * 1.5) + 1))):
            tileWorldX = tileX / 2 + math.ceil(calculatedX / tileSize)
            tileWorldY = tileY - math.ceil(calculatedY / tileSize)

            selectedImage = tiles["mars"]
            if noise([tileWorldX / 4, tileWorldY / 4]) > 0:
                selectedImage = tiles["marsLight"]

            groundGroup = ground
            
            if (tileWorldY % 2 == 0 and tileWorldX % 1 == 0):
                groundGroup = ground2
            elif (tileWorldY % 2 == 1 and tileWorldX % 1 == 0):
                groundGroup = ground3
            
            sprite = pyglet.sprite.Sprite(img = selectedImage, batch = batch, group = groundGroup)
            tileScreenX = tileX * tileSize / 2 + offsetX
            if tileX % 2 == 0:
                tileScreenY = sprite.y = tileY * tileSize / 1.5 + offsetY
            else:
                tileScreenY = tileY * tileSize / 1.5 + tileSize / 1.5 / 2 + offsetY
            sprite.x = tileScreenX
            sprite.y = tileScreenY
            sprite.scale = tileSize / 1024
            
            distanceToTile = distance(tileScreenX + tileSize / 2, tileScreenY + tileSize / 2, mouseX, mouseY)
            if distanceToTile < closestTileMouse:
                closestTileMouse = distanceToTile
                closestTileMouseData["worldX"] = tileWorldX
                closestTileMouseData["worldY"] = tileWorldY

                closestTileMouseData["screenX"] = tileScreenX
                closestTileMouseData["screenY"] = tileScreenY

            sprites.append(sprite)

            tileStructureCode = str(tileWorldX) + "_" + str(tileWorldY)

            if tileStructureCode in structuresGenerated:
                chunkStructure = structuresGenerated[tileStructureCode]
                
                if chunkStructure in chunkStructures:
                    structureData = chunkStructures[chunkStructure]

                    chunkStructureImage = None
                    if structureData["animated"]:
                        chunkStructureImage = structureData["image"][globalAnimationFrame % structureData["columns"]]
                    else:
                        chunkStructureImage = structureData["image"]
                        
                    structureGroup = structures
                    
                    if (tileWorldY % 2 == 0 and tileWorldX % 1 == 0):
                        structureGroup = structures2
                    elif (tileWorldY % 2 == 1 and tileWorldX % 1 == 0):
                        structureGroup = structures3

                    sprite = pyglet.sprite.Sprite(img = chunkStructureImage, batch = batch, group = structureGroup)
                    structureX = tileX * tileSize / 2 + offsetX
                    structureY = 0
                    if tileX % 2 == 0:
                        structureY = tileY * tileSize / 1.5 + offsetY
                    else:
                        structureY = tileY * tileSize / 1.5 + tileSize / 1.5 / 2 + offsetY
                        
                    if chunkStructure == "ironOre" or chunkStructure == "carbonOre":
                        structureX += tileSize / 4
                        structureY += tileSize / 8

                    distanceToOre = distance(structureX + tileSize / 2, structureY + tileSize / 2, window.width / 2, window.height / 2)
                    if distanceToOre < closestInteractable:
                        closestInteractable = distanceToOre
                        closestInteractableData["x"] = tileWorldX
                        closestInteractableData["y"] = tileWorldY

                        closestInteractableData["screenX"] = structureX
                        closestInteractableData["screenY"] = structureY

                        closestInteractableData["data"] = structureData

                        if miningOres == True:
                            if chunkStructures[chunkStructure]["isOre"]:
                                closestInteractableData["type"] = "ToMine"
                            else:
                                closestInteractableData["type"] = "ToBreak"
                                closestInteractableData["item"] = chunkStructure
                        else:
                            if not chunkStructures[chunkStructure]["isOre"]:
                                closestInteractableData["type"] = "ToInteract"
                                closestInteractableData["GUImenu"] = chunkStructure
                            else:
                                closestInteractable = 10000
                

                    sprite.x = structureX
                    sprite.y = structureY

                    sprite.scale = tileSize / 2048

                    sprites.append(sprite)

    batch.draw()

    clickToPlace = False

    if not closestTileMouse == 100000:
        if inventoryItems[selectedHand - 1]["item"] in itemTypes:
            if itemTypes[inventoryItems[selectedHand - 1]["item"]]["canBuild"]:
                tileCode = str(closestTileMouseData["worldX"]) + "_" + str(closestTileMouseData["worldY"])

                if tileCode in structuresGenerated:
                    canPlace = structuresGenerated[tileCode] == 0
                else:
                    canPlace = True

                if canPlace:
                    sprite = pyglet.sprite.Sprite(img = miscImages["place"]["image"][globalAnimationFrame % 13])
                else:
                    sprite = pyglet.sprite.Sprite(img = miscImages["noplace"]["image"][globalAnimationFrame % 13])

                sprite.x = closestTileMouseData["screenX"]
                sprite.y = closestTileMouseData["screenY"]

                sprite.scale = tileSize / 1024

                sprite.draw()

                if canPlace:
                    clickToPlace = True

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
    
    
    if closestInteractable != 100000:
        if closestInteractable < 300:
            hintX = closestInteractableData["screenX"] + tileSize / 4
            hintY = closestInteractableData["screenY"] + tileSize / 2

            ShowUIHint(hintX, hintY, closestInteractableData["type"])

            if not closestInteractableData["type"] == "ToInteract":
                if BreakTime > 0:
                    bar = shapes.Rectangle(
                        x = hintX - 240,
                        y = hintY - 250,
                        width = 500,
                        height = 50,
                        color = ( 100, 100, 100 )
                    )
                    bar.opacity = 150
                    bar.draw()

                    filled = shapes.Rectangle(
                        x = hintX - 235,
                        y = hintY - 245,
                        width = 490 * (BreakTime / closestInteractableData["data"]["breakTime"]),
                        height = 40,
                        color = ( 25, 100, 25 )
                    )
                    filled.opacity = 150
                    filled.draw()
                OpenGUIMenu = 0
            else:
                BreakTime = 0
                if EPressed:
                    OpenGUIMenu = closestInteractableData["GUImenu"]
        else:
            BreakTime = 0
            OpenGUIMenu = 0
    else:
        BreakTime = 0
        OpenGUIMenu = 0

    if closestInteractableData["data"] == 0:
        closestInteractableData["data"] = {
            "breakTime": 1
        }

    if BreakTime >= closestInteractableData["data"]["breakTime"]:
        structuresGenerated[str(closestInteractableData["x"]) + "_" + str(closestInteractableData["y"])] = 0
        if closestInteractableData["data"]["isOre"]:
            for give in closestInteractableData["data"]["gives"]:
                amount = random.randint(give["min"], give["max"])
                giveItem(give["item"], amount)
            BreakTime = 0
        else:
            giveItem(closestInteractableData["item"], 1)
        
    if clickToPlace == True and LMBClicked == True:
        structuresGenerated[tileCode] = inventoryItems[selectedHand - 1]["item"]
        removeItem(inventoryItems[selectedHand - 1]["item"], 1)

    LMBClicked = False
    LMBReleased = False
    RMBClicked = False
    RMBReleased = False
    EPressed = False


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
        chunkStructure = random.choice(["carbonOre", "ironOre", "copperOre"])
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

    drawTutorialPromt()

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
    global gameState, backpackOpened, selectedHand, EPressed

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
        elif symbol == 49: # numbers 1 through 9
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
        elif symbol == 55:
            swapWithSelectedHand(7)
        elif symbol == 56:
            swapWithSelectedHand(8)
        elif symbol == 57:
            swapWithSelectedHand(9)
        elif symbol == key.W:
            keysPressed["w"] = True
        elif symbol == key.A:
            keysPressed["a"] = True
        elif symbol == key.S:
            keysPressed["s"] = True
        elif symbol == key.D:
            keysPressed["d"] = True
        elif symbol == key.E:
            EPressed = True
        elif symbol == key.ESCAPE:
            return pyglet.event.EVENT_HANDLED
        elif symbol == key.N:
            nextTutorialPrompt()
        elif symbol == key.T:
            inventoryItems[selectedHand - 1]["item"] = 0
            inventoryItems[selectedHand - 1]["quantity"] = 1
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
    global LMBHeld, LMBClicked, RMBHeld, RMBClicked

    if gameState == "running":
        if button == mouse.LEFT:
            LMBHeld = True
            LMBClicked = True
        elif button == mouse.RIGHT:
            RMBHeld = True
            RMBClicked = True

@window.event
def on_mouse_release(x, y, button, modifiers):
    global LMBHeld, BreakTime, LMBReleased, RMBHeld, RMBReleased
    
    if gameState == "running":
        if button == mouse.LEFT:
            LMBHeld = False
            BreakTime = 0
            LMBReleased = True
        elif button == mouse.RIGHT:
            RMBHeld = False
            RMBReleased = True

mouseX = 0
mouseY = 0

@window.event
def on_mouse_motion(x, y, movementX, movementY):
    global mouseX, mouseY

    mouseX = x
    mouseY = y

@window.event
def on_mouse_drag(x, y, movementX, movementY, x2, y2):
    global mouseX, mouseY

    mouseX = x
    mouseY = y

# Logs all events that happen
# event_logger = pyglet.window.event.WindowEventLogger()
# window.push_handlers(event_logger)


framerate = 144 # Frames per second

timeSinceAnimationFrame = 0

endElapsed = 0

def update(dt):
    global introElapsed, timeSinceAudioPlayed, timeSinceAnimationFrame, globalAnimationFrame, endElapsed
    
    if gameState == "running":
        updateGame(dt)
        timeSinceAnimationFrame += 1 * dt
        if timeSinceAnimationFrame > 0.1:
            timeSinceAnimationFrame = 0
            globalAnimationFrame += 1
    elif gameState == "intro":
        introElapsed += 1 * dt
        timeSinceAudioPlayed += 1 * dt
    elif gameState == "ending":
        endElapsed += 1 * dt
    elif gameState == "dead":
        endElapsed += 1 * dt

def updateGame(dt):
    global x, y, xMomentum, yMomentum, oxygen, BreakTime, gameState

    movementSpeed = 60 * dt

    oxygenDepletionRate = oxygenDepletePerSecond * ((math.sqrt(xMomentum * xMomentum + yMomentum * yMomentum) + 25) / 25)

    oxygen -= oxygenDepletionRate * dt

    if oxygen <= 0:
        gameState = "dead"

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
    
    if OpenGUIMenu == "drill":
        if len(currentGUIData["slotItems"]) <= 15:
            for i in range(15):
                currentGUIData["slotItems"].append({ "item": 0, "quantity": 1})
        
        if random.random() < 6 * dt:
            index = random.randint(0, 14)
            if currentGUIData["slotItems"][index]["item"] == 0:
                currentGUIData["slotItems"][index]["item"] = random.choice(["carbonChunks", "carbonChunks", "ironChunks", "crudeOil", "copperChunks"])
                currentGUIData["slotItems"][index]["quantity"] = 1
            else:
                currentGUIData["slotItems"][index]["quantity"] += 1

    hasPickaxe = False
    for item in inventoryItems:
        if item["item"] == "pickaxe":
            hasPickaxe = True

    if not hasPickaxe == True:
        giveItem("pickaxe", 1)

    hasItems = True

    materialsForStage = rocketRepairStages[rocketRepairStage]["requires"]
    for materialForStage in materialsForStage:
        if not playerHasMaterials(materialForStage):
            hasItems = False
    
    if hasItems == True:
        loadNextRepairStage()


slotSize = 70
backpackOpened = False

fabricatingMenuSelected = 0

draggingItem = False
draggingData = {}

currentGUIData = {}

def drawInventory():
    global backpackOpened, OpenGUIMenu, draggingItem, LMBClicked, currentGUIData, RMBClicked, RMBHeld

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
    drawSlot(slotSize + 10, 5, slotOneColor, inventoryItems[0], "1", setSlot, 0)

    slotTwoColor = (100, 100, 100)
    if selectedHand == 2:
        slotTwoColor = (150, 150, 150)
    drawSlot(slotSize * 2 + 15, 5, slotTwoColor, inventoryItems[1], "2", setSlot, 1)

    if backpackOpened == True:
        for backpackSlot in range(backpackSlots):
            drawSlot(5, (slotSize + 5) * (1 + backpackSlot) + 5, (80, 80, 80), inventoryItems[2 + backpackSlot], str(backpackSlot + 3), setSlot, backpackSlot + 2)
        
        trashBackground = shapes.Rectangle(
            x = 5,
            y = (slotSize + 5) * (backpackSlots + 1) + 5,
            width = slotSize,
            height = slotSize,
            color = ( 100, 100, 100 )
        )
        if mouseX > 5 and mouseY > (slotSize + 5) * (backpackSlots + 1) + 5 and mouseX < 5 + slotSize and mouseY < (slotSize + 5) * (backpackSlots + 1) + 5 + slotSize:
            trashBackground.opacity = 255
            if LMBReleased == True:
                if not draggingItem == 0:
                    if not draggingData["setSlot"] == 0:
                        draggingData["setSlot"](draggingData["setSlotParameter"], { "item": 0, "quantity": 1 })
        else:
            trashBackground.opacity = 200
        trashBackground.draw()
        
        trashImage = pyglet.sprite.Sprite(img = miscImages["trash"]["image"])
        trashImage.x = 5
        trashImage.y = (slotSize + 5) * (backpackSlots + 1) + 5

        trashImage.scale = slotSize / 1024
        trashImage.draw()

        trashLabel = pyglet.text.Label("T",
            font_name = "Press Start 2P",
            font_size = 15,
            x = 10,
            y = (slotSize + 5) * (backpackSlots + 2) - 5,
            color = (255, 255, 255, 255),
            anchor_x = "left", anchor_y = "top")
        trashLabel.draw()

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
            drawSlot(slotSize + 15 + ((slotSize + 5) * index), (slotSize + 5) * 4, ( 100, 100, 100 ), fabricationRecipe["output"], "", None, None, selectFabricationRecipe, fabricationRecipe, False, False)
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
                drawSlot(slotSize + 15 + ((slotSize + 5) * index), (slotSize + 5) * 3 - 10, hasMaterialsColor, fabricationInput, "", None, None, None, False, False)
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
                
                LMBClicked = False
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

    if not OpenGUIMenu == 0:
        GUIMenu = shapes.Rectangle(
            x = window.width - ((slotSize + 5) * 6), 
            y = 5,
            width = (slotSize + 5) * 6 - 5,
            height = (slotSize + 5) * 4 - 5,
            color = ( 80, 80, 80 )
        )
        GUIMenu.opacity = 200
        GUIMenu.draw()

        labelBackground = shapes.Rectangle(
            x = window.width - ((slotSize + 5) * 6), 
            y = (slotSize + 5) * 4,
            width = 230,
            height = 25,
            color = ( 80, 80, 80 )
        )
        labelBackground.opacity = 200
        labelBackground.draw()

        fabricationLabel = pyglet.text.Label(itemTypes[OpenGUIMenu]["name"],
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 6) + 5,
            y = (slotSize + 5) * 4 + 20,
            color = (255, 255, 255, 255),
            anchor_x = "left", anchor_y = "top")
        fabricationLabel.draw()
    else:
        if "slotItems" in currentGUIData:
            for slotItem in currentGUIData["slotItems"]:
                if not slotItem["item"] == 0:
                    giveItem(slotItem["item"], slotItem["quantity"])

        currentGUIData = {
            "slotItems": []
        }

    if OpenGUIMenu == "smelter":
        if not len(currentGUIData["slotItems"]) == 3:
            currentGUIData["slotItems"] = [{ "item": 0, "quantity": 1}, { "item": 0, "quantity": 1}, { "item": 0, "quantity": 1}]

        smelterRecipes = {
            "ironChunks": "ironBar",
            "carbonChunks": "solidFuel",
            "copperChunks": "copperBar"
        }

        drawSlot(
            window.width - ((slotSize + 5) * 5),
            (slotSize + 5) * 2.5,
            ( 80, 80, 80 ), currentGUIData["slotItems"][0], "", setGUISlot, 0, True, True
        )

        inputLabel = pyglet.text.Label("Input",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 5) + slotSize / 2,
            y = (slotSize + 5) * 2.5 + slotSize,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        inputLabel.draw()
        
        drawSlot(
            window.width - ((slotSize + 5) * 5),
            (slotSize + 5) * 0.5,
            ( 80, 80, 80 ), currentGUIData["slotItems"][1], "", setGUISlot, 1, True, True
        )

        inputLabel = pyglet.text.Label("Fuel",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 5) + slotSize / 2,
            y = (slotSize + 5) * 0.5 + slotSize,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        inputLabel.draw()
        
        drawSlot(
            window.width - ((slotSize + 5) * 2),
            (slotSize + 5) * 1.5,
            ( 80, 80, 80 ), currentGUIData["slotItems"][2], "", setGUISlot, 2, None, None, False, True
        )

        outputLabel = pyglet.text.Label("Output",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 2) + slotSize / 2,
            y = (slotSize + 5) * 1.5 + slotSize,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        outputLabel.draw()

        if currentGUIData["slotItems"][0]["item"] in smelterRecipes:
            if currentGUIData["slotItems"][1]["item"] in ["solidFuel", "carbonChunks"]:
                if currentGUIData["slotItems"][2]["item"] == 0:
                    currentGUIData["slotItems"][2]["item"] = smelterRecipes[currentGUIData["slotItems"][0]["item"]]
                    currentGUIData["slotItems"][2]["quantity"] = 1

                    if currentGUIData["slotItems"][0]["quantity"] > 1:
                        currentGUIData["slotItems"][0]["quantity"] -= 1
                    else:
                        currentGUIData["slotItems"][0]["item"] = 0
                        currentGUIData["slotItems"][0]["quantity"] = 1
                        
                    if currentGUIData["slotItems"][1]["quantity"] > 1:
                        currentGUIData["slotItems"][1]["quantity"] -= 1
                    else:
                        currentGUIData["slotItems"][1]["item"] = 0
                        currentGUIData["slotItems"][1]["quantity"] = 1
                if not currentGUIData["slotItems"][0]["item"] == 0:
                    if currentGUIData["slotItems"][2]["item"] == smelterRecipes[currentGUIData["slotItems"][0]["item"]]:
                        currentGUIData["slotItems"][2]["quantity"] += 1
                        
                        if currentGUIData["slotItems"][0]["quantity"] > 1:
                            currentGUIData["slotItems"][0]["quantity"] -= 1
                        else:
                            currentGUIData["slotItems"][0]["item"] = 0
                            currentGUIData["slotItems"][0]["quantity"] = 1
                            
                        if currentGUIData["slotItems"][1]["quantity"] > 1:
                            currentGUIData["slotItems"][1]["quantity"] -= 1
                        else:
                            currentGUIData["slotItems"][1]["item"] = 0
                            currentGUIData["slotItems"][1]["quantity"] = 1

    elif OpenGUIMenu == "drill":
        if len(currentGUIData["slotItems"]) < 15:
            for i in range(15):
                currentGUIData["slotItems"].append({ "item": 0, "quantity": 1})

        drillOutputs = 15
        
        outputLabel = pyglet.text.Label("Outputs",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 2.5) - slotSize / 2,
            y = (slotSize + 5) * 4 - slotSize / 2,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        outputLabel.draw()

        for output in range(drillOutputs):
            drawSlot(
                window.width - ((slotSize + 5) * (5 - output % 5)) - slotSize / 2,
                (slotSize + 5) * (3 - math.floor(output / 5)) - slotSize / 2,
                ( 80, 80, 80 ), currentGUIData["slotItems"][output], "", setGUISlot, output, None, None, False, True
            )
    elif OpenGUIMenu == "coilMaker":
        if not len(currentGUIData["slotItems"]) == 2:
            currentGUIData["slotItems"] = [{ "item": 0, "quantity": 1}, { "item": 0, "quantity": 1}]

        coilMakerRecipes = {
            "copperBar": "copperWire"
        }

        drawSlot(
            window.width - ((slotSize + 5) * 5),
            (slotSize + 5) * 1.5,
            ( 80, 80, 80 ), currentGUIData["slotItems"][0], "", setGUISlot, 0, True, True
        )

        inputLabel = pyglet.text.Label("Input",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 5) + slotSize / 2,
            y = (slotSize + 5) * 1.5 + slotSize,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        inputLabel.draw()
        
        drawSlot(
            window.width - ((slotSize + 5) * 2),
            (slotSize + 5) * 1.5,
            ( 80, 80, 80 ), currentGUIData["slotItems"][1], "", setGUISlot, 1, None, None, False, True
        )

        outputLabel = pyglet.text.Label("Output",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 2) + slotSize / 2,
            y = (slotSize + 5) * 1.5 + slotSize,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        outputLabel.draw()

        if currentGUIData["slotItems"][0]["item"] in coilMakerRecipes:
            if currentGUIData["slotItems"][1]["item"] == 0:
                currentGUIData["slotItems"][1]["item"] = coilMakerRecipes[currentGUIData["slotItems"][0]["item"]]
                currentGUIData["slotItems"][1]["quantity"] = 1

                if currentGUIData["slotItems"][0]["quantity"] > 1:
                    currentGUIData["slotItems"][0]["quantity"] -= 1
                else:
                    currentGUIData["slotItems"][0]["item"] = 0
                    currentGUIData["slotItems"][0]["quantity"] = 1
            if not currentGUIData["slotItems"][0]["item"] == 0:
                if currentGUIData["slotItems"][1]["item"] == coilMakerRecipes[currentGUIData["slotItems"][0]["item"]]:
                    currentGUIData["slotItems"][1]["quantity"] += 1
                    
                    if currentGUIData["slotItems"][0]["quantity"] > 1:
                        currentGUIData["slotItems"][0]["quantity"] -= 1
                    else:
                        currentGUIData["slotItems"][0]["item"] = 0
                        currentGUIData["slotItems"][0]["quantity"] = 1
    elif OpenGUIMenu == "oilRefinery":
        if len(currentGUIData["slotItems"]) <= 1:
            currentGUIData["slotItems"] = [{ "item": 0, "quantity": 1}, { "item": 0, "quantity": 1}]

        coilMakerRecipes = {
            "crudeOil": "fuel"
        }

        drawSlot(
            window.width - ((slotSize + 5) * 5),
            (slotSize + 5) * 1.5,
            ( 80, 80, 80 ), currentGUIData["slotItems"][0], "", setGUISlot, 0, True, True
        )

        inputLabel = pyglet.text.Label("Input",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 5) + slotSize / 2,
            y = (slotSize + 5) * 1.5 + slotSize,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        inputLabel.draw()
        
        drawSlot(
            window.width - ((slotSize + 5) * 2),
            (slotSize + 5) * 1.5,
            ( 80, 80, 80 ), currentGUIData["slotItems"][1], "", setGUISlot, 1, None, None, False, True
        )

        outputLabel = pyglet.text.Label("Output",
            font_name = "Press Start 2P",
            font_size = 15,
            x = window.width - ((slotSize + 5) * 2) + slotSize / 2,
            y = (slotSize + 5) * 1.5 + slotSize,
            color = (255, 255, 255, 255),
            anchor_x = "center", anchor_y = "bottom")
        outputLabel.draw()

        if currentGUIData["slotItems"][0]["item"] in coilMakerRecipes:
            if currentGUIData["slotItems"][1]["item"] == 0:
                currentGUIData["slotItems"][1]["item"] = coilMakerRecipes[currentGUIData["slotItems"][0]["item"]]
                currentGUIData["slotItems"][1]["quantity"] = 1

                if currentGUIData["slotItems"][0]["quantity"] > 1:
                    currentGUIData["slotItems"][0]["quantity"] -= 1
                else:
                    currentGUIData["slotItems"][0]["item"] = 0
                    currentGUIData["slotItems"][0]["quantity"] = 1
            if not currentGUIData["slotItems"][0]["item"] == 0:
                if currentGUIData["slotItems"][1]["item"] == coilMakerRecipes[currentGUIData["slotItems"][0]["item"]]:
                    currentGUIData["slotItems"][1]["quantity"] += 1
                    
                    if currentGUIData["slotItems"][0]["quantity"] > 1:
                        currentGUIData["slotItems"][0]["quantity"] -= 1
                    else:
                        currentGUIData["slotItems"][0]["item"] = 0
                        currentGUIData["slotItems"][0]["quantity"] = 1

    if not draggingItem == 0:
        drawSlot(mouseX - slotSize / 2, mouseY - slotSize / 2, (0, 0, 0), draggingItem, "", None, None, None, None, False, False, 0)
        if not LMBHeld and not RMBHeld:
            if not draggingData["complete"] and draggingData["half"]:
                draggingData["item"]["quantity"] = draggingData["item"]["quantity"] + draggingItem["otherQuantity"]
                draggingData["setSlot"](draggingData["setSlotParameter"], draggingData["item"])
            draggingItem = 0

    index = 0
    requiredLabel = pyglet.text.Label("Required",
        font_name = "Press Start 2P",
        font_size = 15,
        x = 5,
        y = window.height - 5,
        color = (255, 255, 255, 255),
        anchor_x = "left", anchor_y = "top")
    requiredLabel.draw()
    for requiredItem in rocketRepairStages[rocketRepairStage]["requires"]:
        drawSlot((slotSize + 5) * index + 5, window.height - 30 - slotSize, (80, 80, 80), requiredItem, "", None, None, None, None, False, False)
        index += 1

def setGUISlot(slot, item):
    global currentGUIData
    
    if len(currentGUIData["slotItems"]) > slot:
        currentGUIData["slotItems"][slot] = item

def setSlot(slot, item):
    inventoryItems[slot] = item

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

def drawSlot(slotX, slotY, color, item, label, setSlot, setSlotParameter, clickCallback = None, callbackParameters = None, canDragTo = True, canDragFrom = True, opacity = 200):
    global LMBClicked, LMBReleased, RMBClicked, RMBReleased, draggingItem, draggingData

    slotSquare = shapes.Rectangle(
        x = slotX, 
        y = slotY,
        width = slotSize,
        height = slotSize,
        color = color
    )
    if mouseX > slotX and mouseY > slotY and mouseX < slotX + slotSize and mouseY < slotY + slotSize:
        if opacity == 200:
            slotSquare.opacity = 255
        else:
            slotSquare.opacity = opacity
        
        if not item["item"] == 0:
            slotItemLabel = pyglet.text.Label(itemTypes[item["item"]]["name"],
                font_name = "Press Start 2P",
                font_size = 15,
                x = slotX + 5,
                y = slotY - 5,
                color = (255, 255, 255, 255),
                anchor_x = "left", anchor_y = "top")
            slotItemLabel.draw()

        if LMBClicked == True or RMBClicked == True:
            if canDragFrom == True:
                draggingData["setSlot"] = setSlot
                draggingData["setSlotParameter"] = setSlotParameter
                draggingData["complete"] = False
                if RMBClicked == True and not item["quantity"] <= 1:
                    draggingItem = item.copy()
                    draggingData["item"] = item.copy()
                    draggingData["item"]["quantity"] = math.ceil(draggingData["item"]["quantity"] / 2)
                    item["quantity"] = math.floor(draggingItem["quantity"] / 2)
                    draggingItem["otherQuantity"] = math.floor(draggingItem["quantity"] / 2)
                    draggingItem["quantity"] = math.ceil(draggingItem["quantity"] / 2)
                    draggingData["half"] = True
                else:
                    draggingItem = item
                    draggingData["item"] = item
                    draggingData["half"] = False
                draggingData["slotX"] = slotX
                draggingData["slotY"] = slotY
            else:
                if not clickCallback == None:
                    if callbackParameters == None:
                        clickCallback()
                    else:
                        clickCallback(callbackParameters)
            
        if LMBReleased == True or RMBReleased == True:
            if canDragTo == True:
                if not setSlot == None:
                    if not draggingItem == 0:
                            if not (slotX == draggingData["slotX"] and  slotY == draggingData["slotY"]):
                                draggingData["complete"] = True
                                if draggingData["item"]["item"] == item["item"]:
                                    newStack = draggingData["item"]
                                    newStack["quantity"] += item["quantity"]
                                    setSlot(setSlotParameter, newStack)
                                    if not draggingData["half"]:
                                        if not draggingData["setSlot"] == 0:
                                            draggingData["setSlot"](draggingData["setSlotParameter"], { "item": 0, "quantity": 1 })
                                else:
                                    if not (draggingData["half"] and not item["item"] == 0): 
                                        setSlot(setSlotParameter, draggingData["item"])
                                        if not draggingData["half"]:
                                            if not draggingData["setSlot"] == 0:
                                                draggingData["setSlot"](draggingData["setSlotParameter"], item)
        
        LMBReleased = False
        LMBClicked = False
    else:
        slotSquare.opacity = opacity
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

def loadNextRepairStage():
    global rocketRepairStage, tutorialPromptQueue

    if rocketRepairStage >= 0:
        materialsForStage = rocketRepairStages[rocketRepairStage]["requires"]
        for materialForStage in materialsForStage:
            removeItem(materialForStage["item"], materialForStage["quantity"])

    rocketRepairStage += 1
    if rocketRepairStage >= len(rocketRepairStages):
        # End the game. Show a message from us :)
        endGame()
        rocketRepairStage -= 1
        return

    tutorialPromptQueue = rocketRepairStages[rocketRepairStage]["tutorialPrompts"]

def drawTutorialPromt():
    global LMBClicked

    if len(tutorialPromptQueue) > 0:
        tutorialPromt = tutorialPromptQueue[0]

        tutorialPromtBack = shapes.Rectangle(
            x = window.width / 2 - 300, 
            y = window.height - 175,
            width = 600,
            height = 170,
            color = ( 100, 100, 100 )
        )
        tutorialPromtBack.opacity = 200
        tutorialPromtBack.draw()

        tutorialPromptTitle = pyglet.text.Label(tutorialPromt["title"],
            font_name = "Press Start 2P",
            font_size = 20,
            x = window.width / 2 - 295,
            y = window.height - 10,
            color = (255, 255, 255, 255),
            anchor_x = "left", anchor_y = "top")
        tutorialPromptTitle.draw()
        
        index = 0
        for line in tutorialPromt["description"].split("\n"):
            tutorialPromptContent = pyglet.text.Label(line,
                font_name = "Press Start 2P",
                font_size = 15,
                x = window.width / 2 - 295,
                y = window.height - 60 - (index * 25),
                color = (255, 255, 255, 255),
                anchor_x = "left", anchor_y = "top")
            tutorialPromptContent.draw()
            index += 1

        nextImage = pyglet.sprite.Sprite(img = UIImages["play"])
        nextImage.scale = 32 / 1024
        nextImage.x = window.width / 2 + 260
        nextImage.y = window.height - 170
        nextImage.draw()

        if mouseX > window.width / 2 + 260 and mouseX < window.width / 2 + 260 + 32 and mouseY > window.height - 170 and mouseY < window.height - 170 + 32:
            if LMBClicked:
                LMBClicked = False
                nextTutorialPrompt()
        
        nextLabel = pyglet.text.Label("N",
            font_name = "Press Start 2P",
            font_size = 20,
            x = window.width / 2 + 260,
            y = window.height - 150,
            color = (255, 255, 255, 255),
            anchor_x = "left", anchor_y = "bottom")
        nextLabel.draw()

def nextTutorialPrompt():
    if len(tutorialPromptQueue) > 0:
        tutorialPromptQueue.pop(0)

loadNextRepairStage()

# THIS CODE WAS MADE AFTER THE GAME JAM FINISHED. IT DOES NOT INCLUDE ANY GAMEPLAY, ONLY A MESSAGE FROM US.
endElapsed = 0

def endGame():
    global gameState

    gameState = "ending"

def drawEndScreen():
    endMessage = [
        "Thank you so much for playing our game.",
        "",
        "",
        "Unfortunately, we didn't get to implement",
        "everything we wanted to, although we did try.",
        "We hope you enjoyed playing it as much as we",
        "enjoyed making it.",
        "",
        "",
        "Press ESC to close this window."
    ]

    if endElapsed > 2:
        index = 0
        for message in endMessage:
            if endElapsed > 4 + index * 0.6:
                label = pyglet.text.Label(message,
                        font_name = "Press Start 2P",
                        font_size = 20,
                        x = window.width / 2,
                        y = window.height - 30 - (30 * index),
                        color = (255, 255, 255, round(max(((endElapsed - (4 + index * 0.6))) / 2 * 255, 0))),
                        anchor_x = "center", anchor_y = "top")
                        
                label.draw()

            index += 1
    else:
        cover = shapes.Rectangle(
            x = 0,
            y = 0,
            width = window.width,
            height = window.height,
            color = ( 0, 0, 0 )
        )
        cover.opacity = endElapsed * (255 / 2)
        cover.draw()

# BACK TO REGULAR CODE

pyglet.clock.schedule_interval(update, 1 / framerate)

pyglet.app.run()