game = {
    "unversioned_name": "runner",
    "max_width": 1200.0,
    "max_height": 1000.0,
    "editor_picker_cell_width": 32.0 * 1.25,
    "roles" : {
        "level": {
            ('levelproxy 00.01', 'level 00.01'): {
                # editor required, excluding ingame_type_id
                'width': 1200.0,
                'height': 1000.0,

                "others": {
                    # ingame required, excluding position and *_type_id 
                    }
                }
            },
        "actor": {
            # paths are relative to the path to resources set in start_editor.py
            ('actorproxy 00.01', 'player 00.01'): {
                # editor required, excluding position and ingame_type_id
                'editor_img': 'goodguy.png',
                'visible_width':  32.0,
                # ingame required
                'others': {},
                }
            ,
            ('actorproxy 00.01', 'wanderer 00.01'): {
                'editor_img': 'badguy_1.png',
                'visible_width':  32.0,
                'others': {},
                }
            ,
            ('actorproxy 00.01', 'chained mons 00.01'): {
                'editor_img': 'badguy_2.png',
                'visible_width':  32.0,
                'others': {},
                }
            ,
            ('actorproxy 00.01', 'tree 00.01'): {
                'editor_img': 'tree.png',
                'visible_width':  32.0,
                'others': {},       
                }
            ,
            ('actorproxy 00.01', 'jewel 00.01'): {
                'editor_img': 'jewel_generic.png',
                'visible_width':  32.0,
                'others': {},
                }
            ,
        }
    }
}
