import pyglet

window = pyglet.window.Window(width = 1920, height = 1080, resizable = True, caption="Amazing game")

x = 0
y = 0

xMomentum = 0
yMomentum = 0

pyglet.font.add_file('assets/fonts/Poppins-Regular.ttf')
pyglet.font.load('Poppins')

marsTile = pyglet.image.load('assets/images/tiles/mars.png')

tileSize = 256

@window.event
def on_draw():
    window.clear()

    label = pyglet.text.Label("Hello, world! Amazing!",
        font_name = "Poppins",
        font_size = 40,
        x = window.width / 2,
        y = window.height,
        color = (100, 200, 100, 200),
        anchor_x = "center", anchor_y = "top")

    offsetX = round(-x % tileSize)
    offsetY = round(y % tileSize / 1.5)

    for tileX in range(-3, round(window.width / tileSize * 2) + 1):
        for tileY in range(-2, round(window.height / tileSize * 1.5) + 1):
            sprite = pyglet.sprite.Sprite(img=marsTile)
            sprite.x = tileX * tileSize / 2 + offsetX
            if tileX % 2 == 0:
                sprite.y = tileY * tileSize / 1.5 + offsetY
            else:
                sprite.y = tileY * tileSize / 1.5 + tileSize / 1.5 / 2 + offsetY
            sprite.scale = tileSize / 1024
            sprite.draw()

    label.draw()

from pyglet.window import key

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
    global x, y, xMomentum, yMomentum

    movementSpeed = 120 / framerate

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

pyglet.clock.schedule_interval(update, 1 / framerate)

pyglet.app.run()