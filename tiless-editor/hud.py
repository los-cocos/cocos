from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.menu import Menu, MenuItem, BOTTOM, CENTER, RIGHT

from cocos.widget_container import *
from cocos.widget import *
from cocos.widget_buttons import *
from cocos.widget_event_dispatcher import *

from cocos.director import director

TOP_BAR_HEIGHT = 32
BOTTOM_BAR_HEIGHT = 32

class LayerMenu(Menu):
    def __init__(self, hud):
        super(LayerMenu, self).__init__()
        self.hud = hud
        self.menu_valign = BOTTOM
        self.menu_halign = RIGHT
        self.font_item['font_size'] = 12
        self.font_item_selected['font_size'] = 14

        self.labels = [i.label
                       for i in hud.editor.layers.get_children()
                       if hasattr(i, 'label')]
        
        self.items = [MenuItem(label, self.on_quit) for label in self.labels]
        self.items += [MenuItem("New %s layer"%layer_type,
                                lambda: self.create_layer(layer_type))
                       for layer_type in self.hud.editor.layer_types]
        self.create_menu(self.items)

    def create_layer(self, layer_type):
        layer = self.hud.editor.layer_types[layer_type].get_new_layer()
        layer_num = len(self.hud.editor.layers.layers)
        self.hud.editor.layers.add_layer(
            "%s layer (%s)" % (layer_type, layer_num),
            layer_num, layer)
        self.hud.editor.set_current_layer(layer_num)
        self.hud.hide_layers_menu()

    def on_quit(self):
        self.hud.editor.set_current_layer (self.selected_index)
        self.hud.hide_layers_menu()

class HUDLayer(Layer):
    is_event_handler = True
    def __init__(self, editor):
        super(HUDLayer, self).__init__()
        atts = dict(color=(255,255,255,255), font_size=14,
                anchor_x='right', anchor_y='bottom')
        x, y = director.get_window_size()
        self.hud_x = x - 5
        self.hud_y = y - 20
        self.pointerLabel = Label('0,0', position=(self.hud_x, self.hud_y),
                                  **atts)
        self.add(self.pointerLabel, z=1)
        if editor.current_layer is not None:
            self.layerNameLabel = Label(editor.current_layer.label,
                                    position=(self.hud_x - 140, self.hud_y), **atts)
        else:
            self.layerNameLabel = Label("<no layers>",
                                    position=(self.hud_x - 140, self.hud_y), **atts)
        self.add(self.layerNameLabel, z=1)
        self.editor = editor
        self.showingLayerMenu = False

        translucent = ColorLayer( 64,64,64,192, x, TOP_BAR_HEIGHT)
        translucent.position = (0,y-TOP_BAR_HEIGHT)
        self.add( translucent, name="top-bar" )

        translucent = ColorLayer( 64,64,64,192, x, BOTTOM_BAR_HEIGHT)
        translucent.position = (0,0)
        self.add( translucent, name="bottom-bar" )


        self.add_mode_buttons()

    def add_mode_buttons( self ):

        # NEW BUTTONS
        x, y = director.get_window_size()

        dispatcher = CCWidgetEventDispatcher()
        self.add( dispatcher )

        group = CCButtonGroup()
        group.position = (4,y-32)
        self.add( group, z=1 )

        # edit
        button = CCRadioButton(normal_icon='resources/mode-edit-unselected.png',
                                selected_icon = 'resources/mode-edit-selected.png',
                                clicked_callback=self.callback_mode_edit)
        button.position = (0,0)
        group.add( button )
        button.checked = True

        # camera
        button = CCRadioButton(normal_icon='resources/mode-camera-unselected.png',
                                selected_icon = 'resources/mode-camera-selected.png',
                                clicked_callback=self.callback_mode_camera)
        button.position = (36,0)
        group.add( button )

        # stamp
        button = CCRadioButton(normal_icon='resources/mode-stamp-unselected.png',
                                selected_icon = 'resources/mode-stamp-selected.png',
                                clicked_callback=self.callback_mode_stamp)
        group.add( button )
        button.position = (36*2,0)
        dispatcher.add_widget( group )


    def update(self):
        x, y = self.editor.layers.pointer_to_world(*self.editor.mouse_position)
        self.pointerLabel.element.text = "%d,%d" % (x,y)
        if self.editor.current_layer is not None:
            self.layerNameLabel.element.text = self.editor.current_layer.label
        else:
            self.layerNameLabel.element.text = "<no layers>"

    def on_mouse_press(self, x, y, button, modifiers):
        X, Y = self.layerNameLabel.position
        if X - 70 < x < X and Y < y < Y + 20:
            if not self.showingLayerMenu:
                self.show_layers_menu()

    def show_layers_menu(self):
        self.remove(self.layerNameLabel)
        self.layerMenu = LayerMenu(self)
        self.layerMenu.position = -140, 0
        self.add(self.layerMenu)
        self.showingLayerMenu = True

    def hide_layers_menu(self):
        self.showingLayerMenu = False
        self.add(self.layerNameLabel)
        self.remove(self.layerMenu)
        self.update()


#
# Callbacks
#
    def callback_mode_edit( self, sender ):
        self.editor.switch_mode('edit')

    def callback_mode_camera( self, sender ):
        self.editor.switch_mode('camera')

    def callback_mode_stamp( self, sender ):
        self.editor.switch_mode('stamp')
