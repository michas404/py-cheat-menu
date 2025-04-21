import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
import moderngl
import time
import numpy as np
import json
from pathlib import Path

def create_snowflakes(count, window_width, window_height):
    snowflakes = {
        "x": np.random.uniform(0, window_width, count),
        "y": np.random.uniform(-300, window_height + 300, count),
        "size": np.random.uniform(3, 8, count),
        "speed": np.random.uniform(3, 8, count),
    }
    return snowflakes

def update_snowflakes(snowflakes, window_width, window_height):
    snowflakes["y"] += snowflakes["speed"]
    snowflakes["size"] *= 0.99
    snowflakes["size"] = np.maximum(snowflakes["size"], 1.0)
    reset_indices = (snowflakes["y"] > window_height + 300) | (snowflakes["size"] <= 1.0)
    snowflakes["x"][reset_indices] = np.random.uniform(0, window_width, reset_indices.sum())
    snowflakes["y"][reset_indices] = np.random.uniform(-300, -50, reset_indices.sum())
    snowflakes["size"][reset_indices] = np.random.uniform(3, 8, reset_indices.sum())
    snowflakes["speed"][reset_indices] = np.random.uniform(3, 8, reset_indices.sum())

def draw_snowflakes(snowflakes, draw_list):
    for x, y, size in zip(snowflakes["x"], snowflakes["y"], snowflakes["size"]):
        draw_list.add_circle_filled(x, y, size, imgui.get_color_u32_rgba(1, 1, 1, 0.8))

def set_custom_style():
    style = imgui.get_style()
    colors = style.colors
    style.window_rounding = 10
    style.frame_rounding = 8
    style.child_rounding = 8
    style.popup_rounding = 8
    style.grab_rounding = 12
    style.scrollbar_rounding = 8
    style.window_border_size = 1
    style.frame_border_size = 1
    style.item_spacing = (12, 10)
    style.item_inner_spacing = (10, 8)
    style.window_padding = (15, 15)
    style.frame_padding = (10, 5)
    colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.12, 0.12, 0.12, 0.7)
    colors[imgui.COLOR_FRAME_BACKGROUND] = (0.18, 0.18, 0.18, 0.7)
    colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.22, 0.22, 0.22, 0.7)
    colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = (0.28, 0.28, 0.28, 0.7)
    colors[imgui.COLOR_BUTTON] = (0.2, 0.2, 0.2, 0.7)
    colors[imgui.COLOR_BUTTON_HOVERED] = (0.3, 0.3, 0.3, 0.7)
    colors[imgui.COLOR_BUTTON_ACTIVE] = (0.4, 0.4, 0.4, 0.7)
    colors[imgui.COLOR_HEADER] = (0.2, 0.2, 0.2, 0.7)
    colors[imgui.COLOR_HEADER_HOVERED] = (0.3, 0.3, 0.3, 0.7)
    colors[imgui.COLOR_HEADER_ACTIVE] = (0.4, 0.4, 0.4, 0.7)
    colors[imgui.COLOR_CHECK_MARK] = (1.0, 1.0, 1.0, 1)
    colors[imgui.COLOR_TEXT] = (1.0, 1.0, 1.0, 1)
    colors[imgui.COLOR_TEXT_DISABLED] = (0.5, 0.5, 0.5, 1)
    colors[imgui.COLOR_BORDER] = (0.3, 0.3, 0.3, 0.7)
    colors[imgui.COLOR_SLIDER_GRAB] = (0.6, 0.6, 0.6, 0.7)
    colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = (0.8, 0.8, 0.8, 0.7)
    colors[imgui.COLOR_SCROLLBAR_GRAB] = (0.3, 0.3, 0.3, 0.7)
    colors[imgui.COLOR_SCROLLBAR_GRAB_HOVERED] = (0.4, 0.4, 0.4, 0.7)
    colors[imgui.COLOR_SCROLLBAR_GRAB_ACTIVE] = (0.5, 0.5, 0.5, 0.7)

def ensure_configs_folder():
    configs_dir = Path("configs")
    configs_dir.mkdir(exist_ok=True)
    return configs_dir

def get_config_files():
    configs_dir = ensure_configs_folder()
    return sorted([f.stem for f in configs_dir.glob("*.json")])

def save_config(filename, config_data):
    configs_dir = ensure_configs_folder()
    if not filename:
        return False, "config name cannot be empty"
    if not filename.endswith('.json'):
        filename += '.json'
    config_path = configs_dir / filename
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        return True, "config saved successfully"
    except Exception as e:
        return False, f"error saving config: {str(e)}"

def load_config(filename):
    configs_dir = ensure_configs_folder()
    if not filename.endswith('.json'):
        filename += '.json'
    config_path = configs_dir / filename
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f), "config loaded successfully"
        return None, "config file not found"
    except Exception as e:
        return None, f"error loading config: {str(e)}"

def create_default_config():
    configs_dir = ensure_configs_folder()
    default_config_path = configs_dir / "default.json"
    
    if not default_config_path.exists():
        default_config = {
            "aimbot_active": True,
            "trigger": False,
            "visibility_check": True,
            "fov": 70,
            "fov_changer": True,
            "presets_index": 0,
            "trigger_fov": 0,
            "silent_aim": False,
            "prediction": False,
            "target_priority": 0,
            "cframe": 0.0,
            "cframe_check": False,
            "predx": 0,
            "predy": 0,
            "silent_fov": 0,
            "spinbot_check": False,
            "spinbot_speed": 3.0,
            "selected_parts": {
                "head": False,
                "torso": False,
                "right_arm": False,
                "left_arm": False,
                "right_leg": False,
                "left_leg": False,
            }
        }
        save_config("default.json", default_config)

def main():
    create_default_config()
    
    aimbot_active = True
    trigger = False
    visibility_check = True
    fov = 70
    fov_changer = True
    presets_index = 0
    trigger_fov = 0
    presets = ["legit", "semi-legit", "rage"]
    silent_aim = False
    prediction = False
    target_priority = 0
    cframe = 0.0
    cframe_check = False
    predx = 0
    predy = 0
    silent_fov = 0
    spinbot_check = False
    spinbot_speed = 3.0
    selected_parts = {
        "head": False,
        "torso": False,
        "right_arm": False,
        "left_arm": False,
        "right_leg": False,
        "left_leg": False,
    }
    
    if not glfw.init():
        raise Exception("glfw error")
    
    primary_monitor = glfw.get_primary_monitor()
    video_mode = glfw.get_video_mode(primary_monitor)
    screen_width = video_mode.size.width
    screen_height = video_mode.size.height

    taskbar_height = 40
    adjusted_height = screen_height - taskbar_height

    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    
    window = glfw.create_window(screen_width, adjusted_height, "", None, None)
    if not window:
        glfw.terminate()
        raise Exception("glfw window creation error")
    
    glfw.set_window_pos(window, 0, 0)
    glfw.make_context_current(window)

    imgui.create_context()
    impl = GlfwRenderer(window)
    ctx = moderngl.create_context()
    io = imgui.get_io()
    set_custom_style()
    snowflakes = create_snowflakes(100, screen_width, adjusted_height)
    
    transitions = {part: 0.0 for part in selected_parts}
    config_files = get_config_files()
    new_config_name = ""
    show_save_config_window = False
    show_load_config_window = False
    config_status_message = ""
    last_time = time.time()
    target_fps = 144
    aimbot_window_width = 420
    aimbot_window_height = 450
    misc_window_width = 420
    new_window_width = 420
    new_window_height = 450
    new_window_x = (screen_width - (aimbot_window_width + misc_window_width + new_window_width + 40)) // 2
    aimbot_x = new_window_x + new_window_width + 20
    aimbot_y = (adjusted_height - aimbot_window_height) // 2
    misc_x = aimbot_x + aimbot_window_width + 20
    config_window_width = 450
    config_window_height = 200
    config_window_y = 50

    def lerp_color(transition):
        color = 1.0 - (0.5 * transition)
        return imgui.get_color_u32_rgba(color, color, color, 1)

    visible = False
    home_pressed = False
    fade_alpha = 0.0
    fade_target = 0.0
    fade_speed = 0.08

    while not glfw.window_should_close(window):
        glfw.poll_events()

        key_state = glfw.get_key(window, glfw.KEY_HOME)
        if key_state == glfw.PRESS and not home_pressed:
            visible = not visible
            fade_target = 1.0 if visible else 0.0
        home_pressed = key_state == glfw.PRESS

        if abs(fade_alpha - fade_target) > 0.01:
            fade_alpha += (fade_target - fade_alpha) * fade_speed
        else:
            fade_alpha = fade_target

        if fade_alpha < 0.01:
            ctx.clear(0.0, 0.0, 0.0, 0.0)
            glfw.swap_buffers(window)
            continue

        current_time = time.time()
        delta_time = current_time - last_time
        if delta_time < 1 / target_fps:
            time.sleep((1 / target_fps) - delta_time)
        last_time = time.time()

        impl.process_inputs()
        ctx.clear(0.0, 0.0, 0.0, fade_alpha * 0.78)
        imgui.new_frame()
        imgui.push_style_var(imgui.STYLE_ALPHA, fade_alpha)

        update_snowflakes(snowflakes, screen_width, adjusted_height)
        draw_list = imgui.get_background_draw_list()
        draw_snowflakes(snowflakes, draw_list)

        imgui.set_next_window_position(new_window_x, aimbot_y)
        imgui.set_next_window_size(new_window_width, new_window_height)
        imgui.begin("part selector", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_TITLE_BAR)
        imgui.text("click on a part to select it")
        imgui.separator()

        draw_list = imgui.get_window_draw_list()
        base_x, base_y = imgui.get_cursor_screen_pos()

        center_x = base_x + (new_window_width // 2) - 60
        center_y = base_y + (new_window_height // 2) - 150

        for part, rect in [
            ("head", (center_x + 25, center_y, center_x + 75, center_y + 50)),
            ("torso", (center_x + 25, center_y + 60, center_x + 75, center_y + 130)),
            ("right_arm", (center_x + 80, center_y + 60, center_x + 100, center_y + 130)),
            ("left_arm", (center_x + 0, center_y + 60, center_x + 20, center_y + 130)),
            ("right_leg", (center_x + 55, center_y + 140, center_x + 75, center_y + 200)),
            ("left_leg", (center_x + 25, center_y + 140, center_x + 45, center_y + 200)),
        ]:
            target = 1.0 if selected_parts[part] else 0.0
            transitions[part] += (target - transitions[part]) * 0.1

            color = lerp_color(transitions[part])

            draw_list.add_rect_filled(*rect, color)

            if imgui.is_mouse_clicked(0):
                mouse_pos = imgui.get_mouse_pos()
                if rect[0] <= mouse_pos.x <= rect[2] and rect[1] <= mouse_pos.y <= rect[3]:
                    selected_parts[part] = not selected_parts[part]

        text_y = center_y + 220
        selected_text = "selected parts: "
        selected_list = []

        if selected_parts["head"]:
            selected_list.append("head")
        if selected_parts["torso"]:
            selected_list.append("torso")
        if selected_parts["left_arm"]:
            selected_list.append("left arm")
        if selected_parts["right_arm"]:
            selected_list.append("right arm")
        if selected_parts["left_leg"]:
            selected_list.append("left leg")
        if selected_parts["right_leg"]:
            selected_list.append("right leg")

        if selected_list:
            selected_text += ", ".join(selected_list)
        else:
            selected_text += "none"

        text_width = imgui.calc_text_size(selected_text).x
        text_x = base_x + (new_window_width // 2) - (text_width // 2)
        text_y = center_y + 220

        draw_list.add_text(text_x, text_y, imgui.get_color_u32_rgba(1, 1, 1, 1), selected_text)

        imgui.end()

        imgui.set_next_window_position(aimbot_x, aimbot_y)
        imgui.set_next_window_size(aimbot_window_width, aimbot_window_height)
        imgui.begin("aimbot", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_TITLE_BAR)
        imgui.text("aimbot settings")
        imgui.separator()
        _, aimbot_active = imgui.checkbox("aimbot", aimbot_active)
        _, visibility_check = imgui.checkbox("visibility check", visibility_check)
        imgui.separator()
        _, prediction = imgui.checkbox("prediction", prediction)
        _, predx = imgui.slider_float("prediction x", predx, 0.0, 10.0)
        _, predy = imgui.slider_float("prediction y", predy, 0, 10.0)
        imgui.separator()
        _, silent_aim = imgui.checkbox("silent aim", silent_aim)
        _, silent_fov = imgui.slider_int("silent fov", silent_fov, 0, 300)
        _, target_priority = imgui.combo("target priority", target_priority, ["closest", "lowest hp", "angle", "distance"])
        imgui.separator()
        _, presets_index = imgui.combo("presets", presets_index, presets)
        imgui.separator()
        DONT_DELETE = "".join(chr(x) for x in [104, 116, 116, 112, 115, 58, 47, 47, 100, 111, 99, 115, 46, 109, 105, 99, 104, 97, 115, 46, 108, 111, 108, 47])
        if imgui.button("https:/docs.michas.lol/"):
            import webbrowser
            webbrowser.open(DONT_DELETE)
        imgui.end()

        imgui.set_next_window_position(misc_x, aimbot_y)
        imgui.set_next_window_size(misc_window_width, aimbot_window_height)
        imgui.begin("misc", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_TITLE_BAR)
        imgui.text("misc settings")
        imgui.separator()
        _, cframe_check = imgui.checkbox("cframe", cframe_check)
        _, cframe = imgui.slider_float("cframe speed", cframe, 0.0, 50.0)
        imgui.separator()
        _, trigger = imgui.checkbox("triggerbot", trigger)
        _, trigger_fov = imgui.slider_int("trigger fov", trigger_fov, 0, 300)
        imgui.separator()
        _, spinbot_check = imgui.checkbox("spinbot", spinbot_check)
        _, spinbot_speed = imgui.slider_float("spinbot speed", spinbot_speed, 0.0, 10.0)
        imgui.separator()
        _, fov_changer = imgui.checkbox("fov changer", fov_changer)
        _, fov = imgui.slider_int("fov", fov, 0, 120)
        imgui.separator()

        if imgui.button("save config"):
            show_save_config_window = True
            show_load_config_window = False
            config_files = get_config_files()
            config_status_message = ""
        imgui.same_line()
        if imgui.button("load config"):
            show_load_config_window = True
            show_save_config_window = False
            config_files = get_config_files()
            config_status_message = ""

        imgui.end()

        if show_save_config_window:
            imgui.set_next_window_size(config_window_width, config_window_height)
            imgui.set_next_window_position((screen_width - config_window_width) // 2, config_window_y)
            
            imgui.begin("save config", True, flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_TITLE_BAR)
            
            imgui.text("save config")
            imgui.separator()
            
            imgui.text("config name:")
            imgui.push_item_width(300)
            _, new_config_name = imgui.input_text("##config_name", new_config_name, 256)
            imgui.pop_item_width()
            imgui.same_line()
            if imgui.button("save config"):
                if new_config_name:
                    config_data = {
                        "aimbot_active": aimbot_active,
                        "trigger": trigger,
                        "visibility_check": visibility_check,
                        "fov": fov,
                        "fov_changer": fov_changer,
                        "presets_index": presets_index,
                        "trigger_fov": trigger_fov,
                        "silent_aim": silent_aim,
                        "prediction": prediction,
                        "target_priority": target_priority,
                        "cframe": cframe,
                        "cframe_check": cframe_check,
                        "predx": predx,
                        "predy": predy,
                        "silent_fov": silent_fov,
                        "spinbot_check": spinbot_check,
                        "spinbot_speed": spinbot_speed,
                        "selected_parts": selected_parts
                    }
                    success, message = save_config(new_config_name, config_data)
                    config_status_message = message
                    if success:
                        config_files = get_config_files()
                        new_config_name = ""
            
            if config_status_message:
                imgui.text_colored(config_status_message, 1.0, 0.5 if "error" in config_status_message else 1.0, 0.5)
            
            imgui.separator()
            if imgui.button("close"):
                show_save_config_window = False
                new_config_name = ""
                config_status_message = ""
            
            imgui.end()

        if show_load_config_window:
            imgui.set_next_window_size(config_window_width, config_window_height)
            imgui.set_next_window_position((screen_width - config_window_width) // 2, config_window_y)
            
            imgui.begin("load config", True, flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_TITLE_BAR)
            
            imgui.text("available configs:")
            imgui.separator()
            
            if imgui.begin_child("config_list", height=200):
                if config_files:
                    for config in config_files:
                        if imgui.selectable(config)[0]:
                            loaded_config, message = load_config(config)
                            config_status_message = message
                            if loaded_config:
                                aimbot_active = loaded_config.get("aimbot_active", aimbot_active)
                                trigger = loaded_config.get("trigger", trigger)
                                visibility_check = loaded_config.get("visibility_check", visibility_check)
                                fov = loaded_config.get("fov", fov)
                                fov_changer = loaded_config.get("fov_changer", fov_changer)
                                presets_index = loaded_config.get("presets_index", presets_index)
                                trigger_fov = loaded_config.get("trigger_fov", trigger_fov)
                                silent_aim = loaded_config.get("silent_aim", silent_aim)
                                prediction = loaded_config.get("prediction", prediction)
                                target_priority = loaded_config.get("target_priority", target_priority)
                                cframe = loaded_config.get("cframe", cframe)
                                cframe_check = loaded_config.get("cframe_check", cframe_check)
                                predx = loaded_config.get("predx", predx)
                                predy = loaded_config.get("predy", predy)
                                silent_fov = loaded_config.get("silent_fov", silent_fov)
                                spinbot_check = loaded_config.get("spinbot_check", spinbot_check)
                                spinbot_speed = loaded_config.get("spinbot_speed", spinbot_speed)
                                if "selected_parts" in loaded_config:
                                    for part, state in loaded_config["selected_parts"].items():
                                        selected_parts[part] = state
                                    for part in selected_parts:
                                        transitions[part] = 1.0 if selected_parts[part] else 0.0
                else:
                    imgui.text("no config files found in /configs")
                imgui.end_child()
            
            if config_status_message:
                imgui.text_colored(config_status_message, 1.0, 0.5 if "error" in config_status_message else 1.0, 0.5)
            
            imgui.separator()
            if imgui.button("close"):
                show_load_config_window = False
                config_status_message = ""
            
            imgui.end()

        imgui.pop_style_var()
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()