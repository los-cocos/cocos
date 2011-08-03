game = {
    "unversioned_name": "runner",
    "max_width": 1200.0,
    "max_height": 1000.0,
    # implementation detail with impact in editor mouse picking performance:
    # if all actors have the same visible width, choose the value
    # k = 1.25 * visible_width
    # else you can try k ~ max {actor.visible_width * 1.25 }
    # The later can be too big if there are few intances with big visible_width,
    # then you can exclude outliers before max.
    # Rought guesses are ok, don't spend time here except if the editor mouse
    # selection feels laggy.
    "editor_picker_cell_width": 32.0 * 1.25,
    "roles" : {
        # <role_name>: dict of available variants for this role
        # where 'dict of available variants for this role' have
        # key: value pairs by
        # (editor_type_id, ingame_type_id): param_dict
        # where param_dict carries the info:
        # param_dict = {
        #   key:value pairs mandatory for editor instantiation,
        #   value will be used when doing 'new object' in editor
        #   others = {
        #        key: value pairs needed for ingame instantiation
        #        value will be used when doing 'new object' in editor
        #        }
        #   }
        "level": {
            ('levelproxy 00.01', 'level 00.01'): {
                # editor required, excluding ingame_type_id
                'width': 1200.0,
                'height': 1000.0,

                "others": {
                    # ingame required, excluding position and *_trype_id 
                    }
                }
            },
        "actor": {
            # paths are relative to the path to resources set in start_editor.py
            ('actorproxy 00.01', 'Player 00.01'): {
                # editor required, excluding position and ingame_type_id
                'editor_img': 'goodguy.png',
                'visible_width':  32.0,
                # ingame required
                'others': {},
                }
            ,
            ('actorproxy 00.01', 'Enemy normal 00.01'): {
                'editor_img': 'badguy_1.png',
                'visible_width':  32.0,
                'others': {},
                }
            ,
            ('actorproxy 00.01', 'Enemy charger 00.01'): {
                'editor_img': 'badguy_2.png',
                'visible_width':  32.0,
                'others': {},
                }
            ,
            ('actorproxy 00.01', 'Tree 00.01'): {
                'editor_img': 'tree.png',
                'visible_width':  32.0,
                'others': {},       
                }
            ,
            ('actorproxy 00.01', 'Jewel 00.01'): {
                'editor_img': 'jewel_generic.png',
                'visible_width':  32.0,
                'others': {},
                }
            ,
        }
    }
}
