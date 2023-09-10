    # compose
    ini_entries = ini_read.compose(FILE_INI)
    img_compose_on.set(ini_entries['img_compose_on'])
    img_compose_file.set(ini_entries['img_compose_filename'])
    img_compose_right.set(ini_entries['img_compose_right'])
    img_compose_autoresize.set(ini_entries['img_compose_autoresize'])
    img_compose_color.set(ini_entries['img_compose_color'])
    img_compose_gravity.set(ini_entries['img_compose_gravity'])

    vignette = {'section': 'Compose',
                'on': img_compose_on.get(),
                'filename': img_compose_file.get(),
                'right': img_compose_right.get(),
                'autoresize': img_compose_autoresize.get(),
                'color': img_compose_color.get(),
                'gravity': img_compose_gravity.get()
                }