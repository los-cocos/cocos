# game specific info that editor must known
game = {
    "name": "test",
    "max_width": 1200,
    "max_height": 1000,
    # implementation detail with impact in editor mouse picking performance:
    # if all actors have the same visible width, choose the value
    # k = 1.25 * visible_width
    # else you can try k ~ max {actor.visible_width * 1.25 }
    # The later can be too big if there are few intances with big visible_width,
    # then you can exclude outliers before max.
    # Rought guesses are ok, don't spend time here except if the editor mouse
    # selection feels laggy.
    "editor_picker_cell_width": 32.0 * 1.25,
    "level_type_descriptor": 'Level 00.01', 
    "available_actor_types": {
        # paths are relative to the path to resources set in start_editor.py
        "Player 00.01": {
            'editor_img': 'goodguy.png',
            'visible_width':  32.0,
            'others': {},
            },
        "Enemy normal 00.01": {
            'editor_img': 'badguy_1.png',
            'visible_width':  32.0,
            'others': {},
            },
        "Enemy charger 00.01": {
            'editor_img': 'badguy_2.png',
            'visible_width':  32.0,
            'others': {},
            },
        "Tree 00.01": {
            'editor_img': 'tree.png',
            'visible_width':  32.0,
            'others': {},       
            },
        "Jewel 00.01" : {
            'editor_img': 'jewel_generic.png',
            'visible_width':  32.0,
            'others': {},
            },
        },
                
    }
