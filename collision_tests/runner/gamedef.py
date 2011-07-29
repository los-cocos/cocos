# game specific info that editor must known
game = {
    "name": "test",
    "max_width": 1200,
    "max_height": 1000,
    "min_actor_diameter": 16.0,
    "max_actor_diameter": 64.0,
    "max_jewels": 5, 
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
