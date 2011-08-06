game = {
    "unversioned_name": "Alien Cowboy Zombies",
    "max_width": 1200.0,
    "max_height": 1000.0,
    "editor_picker_cell_width": 32.0 * 1.25,
    "roles" : {
        "level": {
            ('levelproxy 00.01', 'level 00.01'): {
                'width': 1200.0,
                'height': 1000.0,
                'others': {
                    }
                }
            },
        "actor": {
            ('actorproxy 00.01', 'player 00.01'): {
                'editor_img': 'goodguy.png',
                'visible_width':  32.0,
                'others': {
                    },
                }
            ,
            ('actorproxy 00.01', 'enemy 00.01'): {
                'editor_img': 'badguy.png',
                'visible_width':  32.0,
                'others': {
                    },
                }
            ,
            # other actors
        }
    }
}
