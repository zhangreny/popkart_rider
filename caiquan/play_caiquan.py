import argparse
import ctypes
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import win32api
import win32con
import win32gui
from PIL import ImageGrab


ROOT = Path(__file__).resolve().parent
DISPLAY_ID = "DELD1EE"
STOP_FILE = ROOT / "stop.loop"

MOVE_BEATS = {
    "jiandao": "bu",
    "shitou": "jiandao",
    "bu": "shitou",
}
WINNING_MOVE = {loser: winner for winner, loser in MOVE_BEATS.items()}
USER_TEMPLATE = {
    "jiandao": "user-jiandao.png",
    "shitou": "user-shitou.png",
    "bu": "user-bu.png",
}


@dataclass
class Match:
    name: str
    score: float
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self):
        return self.x + self.w // 2, self.y + self.h // 2


def set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def find_display_rect(display_id=DISPLAY_ID):
    for hmon, _hdc, _rect in win32api.EnumDisplayMonitors():
        info = win32api.GetMonitorInfo(hmon)
        device = info["Device"]
        index = 0
        while True:
            try:
                details = win32api.EnumDisplayDevices(device, index)
            except Exception:
                break
            if display_id.upper() in details.DeviceID.upper():
                return info["Monitor"]
            index += 1
    raise RuntimeError(f"Could not find display containing {display_id!r}")


def virtual_origin():
    return (
        win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN),
        win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN),
    )


def screenshot_display(rect):
    vx, vy = virtual_origin()
    img = ImageGrab.grab(all_screens=True)
    left, top, right, bottom = rect
    crop = img.crop((left - vx, top - vy, right - vx, bottom - vy))
    return cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)


def load_template(filename, top_ratio=1.0):
    img = cv2.imread(str(ROOT / filename), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(ROOT / filename)
    if top_ratio < 1.0:
        h = max(1, int(img.shape[0] * top_ratio))
        img = img[:h, :, :]
    return img


TEMPLATES = {
    "entry": load_template("entry.png"),
    "yes": load_template("yes.png"),
    "no": load_template("no.png"),
    "jiandao": load_template("jiandao.png"),
    "shitou": load_template("shitou.png"),
    "bu": load_template("bu.png"),
    # Ignore the bottom count text, because the inventory count changes after clicks.
    "user-jiandao": load_template("user-jiandao.png", top_ratio=0.72),
    "user-shitou": load_template("user-shitou.png", top_ratio=0.72),
    "user-bu": load_template("user-bu.png", top_ratio=0.72),
}


RESULT_TEMPLATES = {
    name: [
        cv2.resize(
            TEMPLATES[name],
            (
                int(TEMPLATES[name].shape[1] * scale),
                int(TEMPLATES[name].shape[0] * scale),
            ),
            interpolation=cv2.INTER_CUBIC,
        )
        for scale in (1.45, 1.50, 1.55, 1.60, 1.65, 1.70)
    ]
    for name in ("jiandao", "shitou", "bu")
}


def best_match(image, name, region=None):
    template = TEMPLATES[name]
    if region:
        x1, y1, x2, y2 = region
        haystack = image[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1
    else:
        haystack = image
        offset_x, offset_y = 0, 0
    result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
    _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
    h, w = template.shape[:2]
    return Match(name, float(max_val), max_loc[0] + offset_x, max_loc[1] + offset_y, w, h)


def best_scaled_match(image, name, region=None):
    templates = RESULT_TEMPLATES[name]
    if region:
        x1, y1, x2, y2 = region
        haystack = image[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1
    else:
        haystack = image
        offset_x, offset_y = 0, 0

    best = None
    for template in templates:
        h, w = template.shape[:2]
        if h > haystack.shape[0] or w > haystack.shape[1]:
            continue
        result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
        match = Match(name, float(max_val), max_loc[0] + offset_x, max_loc[1] + offset_y, w, h)
        if not best or match.score > best.score:
            best = match
    if not best:
        raise RuntimeError(f"No scaled template fits for {name}")
    return best


def all_matches(image, name, threshold=0.78, region=None, min_distance=45):
    template = TEMPLATES[name]
    if region:
        x1, y1, x2, y2 = region
        haystack = image[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1
    else:
        haystack = image
        offset_x, offset_y = 0, 0

    result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
    ys, xs = np.where(result >= threshold)
    candidates = []
    h, w = template.shape[:2]
    for x, y in zip(xs, ys):
        candidates.append(Match(name, float(result[y, x]), int(x + offset_x), int(y + offset_y), w, h))
    candidates.sort(key=lambda item: item.score, reverse=True)

    kept = []
    for candidate in candidates:
        cx, cy = candidate.center
        if all((cx - k.center[0]) ** 2 + (cy - k.center[1]) ** 2 >= min_distance ** 2 for k in kept):
            kept.append(candidate)
    return kept


def move_and_click(abs_x, abs_y):
    abs_x = int(abs_x)
    abs_y = int(abs_y)
    cur_x, cur_y = win32api.GetCursorPos()
    steps = max(12, min(35, int(((abs_x - cur_x) ** 2 + (abs_y - cur_y) ** 2) ** 0.5 / 35)))
    for step in range(1, steps + 1):
        t = step / steps
        eased = t * t * (3 - 2 * t)
        x = int(round(cur_x + (abs_x - cur_x) * eased))
        y = int(round(cur_y + (abs_y - cur_y) * eased))
        if not ctypes.windll.user32.SetCursorPos(x, y):
            time.sleep(0.02)
            win32api.SetCursorPos((x, y))
        time.sleep(0.008)
    time.sleep(0.06)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    time.sleep(0.08)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)


def click_match(rect, match, label):
    left, top, _right, _bottom = rect
    cx, cy = match.center
    abs_x, abs_y = left + cx, top + cy
    print(f"click {label}: score={match.score:.3f} screen=({abs_x},{abs_y})", flush=True)
    move_and_click(abs_x, abs_y)


def wait_for_match(rect, name, threshold=0.78, timeout=12, region=None, poll=0.25):
    end = time.time() + timeout
    last = None
    while time.time() < end:
        image = screenshot_display(rect)
        match = best_match(image, name, region=region)
        last = match
        if match.score >= threshold:
            return image, match
        time.sleep(poll)
    raise TimeoutError(f"Timed out waiting for {name}; best score={last.score:.3f} at {last.center if last else None}")


def find_popkart_rect():
    hwnd = win32gui.FindWindow(None, "PopKart Client")
    if not hwnd:
        return None
    return win32gui.GetWindowRect(hwnd)


def stage_search_region(rect, image):
    window = find_popkart_rect()
    h, w = image.shape[:2]
    if window:
        display_left, display_top, _display_right, _display_bottom = rect
        left, top, right, bottom = window
        width = right - left
        height = bottom - top
        x1 = int(left - display_left + width * 0.65)
        x2 = int(left - display_left + width * 0.83)
        y1 = int(top - display_top + height * 0.32)
        y2 = int(top - display_top + height * 0.60)
    else:
        x1, x2 = int(w * 0.49), int(w * 0.65)
        y1, y2 = int(h * 0.32), int(h * 0.54)
    return max(0, x1), max(0, y1), min(w, x2), min(h, y2)


def infer_stage_from_highlight_y(rect, image, y_center):
    window = find_popkart_rect()
    if window:
        display_left, display_top, _display_right, _display_bottom = rect
        _left, top, _right, bottom = window
        height = bottom - top
        bottom_stage_center = top - display_top + height * 0.560
        row_spacing = height * 0.0332
    else:
        h = image.shape[0]
        bottom_stage_center = h * 0.494
        row_spacing = h * 0.0257
    return int(round((bottom_stage_center - y_center) / row_spacing)) + 1


def detect_current_stage(rect, image=None):
    if image is None:
        image = screenshot_display(rect)
    x1, y1, x2, y2 = stage_search_region(rect, image)
    crop = image[y1:y2, x1:x2]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((hue >= 88) & (hue <= 114) & (sat >= 120) & (val >= 45)).astype(np.uint8)
    row_counts = mask.sum(axis=1)
    row_threshold = max(90, int(mask.shape[1] * 0.42))

    segments = []
    start = None
    for y, count in enumerate(row_counts):
        if count >= row_threshold and start is None:
            start = y
        elif count < row_threshold and start is not None:
            if y - start >= 10:
                segments.append((start, y))
            start = None
    if start is not None and len(row_counts) - start >= 10:
        segments.append((start, len(row_counts)))

    candidates = []
    for start, end in segments:
        band = mask[start:end, :]
        ys, xs = np.where(band > 0)
        if len(xs) == 0:
            continue
        width = int(xs.max() - xs.min() + 1)
        height = int(end - start)
        if not (180 <= width <= 430 and 12 <= height <= 50):
            continue
        fill = float(len(xs)) / float(width * height)
        center_x = int(x1 + xs.min() + width / 2)
        center_y = int(y1 + (start + end) / 2)
        score = width + height * 2 + fill * 100
        candidates.append((score, center_x, center_y, width, height, fill))

    if not candidates:
        raise RuntimeError(f"Could not detect highlighted stage row in region=({x1},{y1},{x2},{y2})")

    candidates.sort(reverse=True)
    _score, center_x, center_y, width, height, fill = candidates[0]
    stage = infer_stage_from_highlight_y(rect, image, center_y)
    if not 1 <= stage <= 7:
        raise RuntimeError(f"Detected highlighted row at y={center_y}, but inferred invalid stage={stage}")
    return stage, Match("stage-highlight", fill, center_x - width // 2, center_y - height // 2, width, height)


def detect_won_stages(rect, image=None):
    if image is None:
        image = screenshot_display(rect)
    window = find_popkart_rect()
    if window:
        display_left, display_top, _display_right, _display_bottom = rect
        left, top, right, bottom = window
        width = right - left
        height = bottom - top
        x1 = int(left - display_left + width * 0.663)
        x2 = int(left - display_left + width * 0.688)
        bottom_stage_center = top - display_top + height * 0.560
        row_spacing = height * 0.0332
    else:
        h, w = image.shape[:2]
        x1 = int(w * 0.515)
        x2 = int(w * 0.535)
        bottom_stage_center = h * 0.494
        row_spacing = h * 0.0257

    won = []
    for stage in range(1, 8):
        center_y = int(round(bottom_stage_center - (stage - 1) * row_spacing))
        y1 = max(0, center_y - 13)
        y2 = min(image.shape[0], center_y + 13)
        crop = image[y1:y2, max(0, x1):min(image.shape[1], x2)]
        if crop.size == 0:
            continue
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        hue = hsv[:, :, 0]
        sat = hsv[:, :, 1]
        val = hsv[:, :, 2]
        blue_count = int(((hue >= 88) & (hue <= 115) & (sat >= 80) & (val >= 80)).sum())
        # Completed rows show a compact blue "win" glyph; the current highlighted
        # row is almost entirely blue and is intentionally excluded here.
        if 50 <= blue_count <= 450:
            won.append(stage)
    return won


def result_card_region(rect, image):
    window = find_popkart_rect()
    h, w = image.shape[:2]
    if window:
        display_left, display_top, _display_right, _display_bottom = rect
        left, top, right, bottom = window
        width = right - left
        height = bottom - top
        x1 = int(left - display_left + width * 0.21)
        x2 = int(left - display_left + width * 0.39)
        y1 = int(top - display_top + height * 0.30)
        y2 = int(top - display_top + height * 0.57)
    else:
        x1, x2 = int(w * 0.17), int(w * 0.31)
        y1, y2 = int(h * 0.34), int(h * 0.56)
    return max(0, x1), max(0, y1), min(w, x2), min(h, y2)


def detect_result_opponent(rect, image):
    region = result_card_region(rect, image)
    matches = [best_scaled_match(image, name, region=region) for name in ("jiandao", "shitou", "bu")]
    matches.sort(key=lambda item: item.score, reverse=True)
    best = matches[0]
    details = ", ".join(f"{m.name}:{m.score:.3f}@{m.center}" for m in matches)
    if best.score < 0.70:
        raise RuntimeError(f"Could not confidently detect result opponent. Candidates: {details}")
    return best.name, best, details


def outcome_for_move(move, opponent):
    if MOVE_BEATS[move] == opponent:
        return "win"
    if move == opponent:
        return "draw"
    return "lose"


def wait_for_stage(rect, timeout=8, poll=0.25):
    end = time.time() + timeout
    last_error = None
    while time.time() < end:
        image = screenshot_display(rect)
        try:
            stage, match = detect_current_stage(rect, image)
            return image, stage, match
        except RuntimeError as exc:
            last_error = exc
        time.sleep(poll)
    raise TimeoutError(f"Timed out waiting for current stage; last error: {last_error}")


def find_reward_confirm_button(rect, image):
    window = find_popkart_rect()
    h, w = image.shape[:2]
    if window:
        display_left, display_top, _display_right, _display_bottom = rect
        left, top, right, bottom = window
        width = right - left
        height = bottom - top
        x1 = int(left - display_left + width * 0.34)
        x2 = int(left - display_left + width * 0.66)
        y1 = int(top - display_top + height * 0.58)
        y2 = int(top - display_top + height * 0.77)
        target_x = int(left - display_left + width * 0.50)
    else:
        x1, x2 = int(w * 0.32), int(w * 0.68)
        y1, y2 = int(h * 0.58), int(h * 0.77)
        target_x = int(w * 0.50)

    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        return None

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((hue >= 88) & (hue <= 114) & (sat >= 80) & (val >= 120)).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    count, _labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    candidates = []
    for index in range(1, count):
        x, y, width, height, area = stats[index]
        if not (90 <= width <= 180 and 32 <= height <= 60):
            continue
        fill = area / float(width * height)
        if fill < 0.80:
            continue
        center_x = int(x1 + centroids[index][0])
        center_y = int(y1 + centroids[index][1])
        if abs(center_x - target_x) > 130:
            continue
        score = fill * 100 - abs(center_x - target_x) / 3 + height
        candidates.append((score, Match("reward-confirm", fill, x1 + int(x), y1 + int(y), int(width), int(height))))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def wait_and_click_reward_confirm(rect, timeout=15, poll=0.25):
    end = time.time() + timeout
    last = None
    while time.time() < end:
        image = screenshot_display(rect)
        match = find_reward_confirm_button(rect, image)
        if match:
            last = match
            click_match(rect, match, "reward confirm")
            return True
        time.sleep(poll)
    print(f"reward confirm not found; last={last}", flush=True)
    return False


def click_banner_fallback():
    window = find_popkart_rect()
    if not window:
        raise RuntimeError("PopKart Client window not found for banner fallback")
    left, top, right, bottom = window
    width = right - left
    height = bottom - top
    # After selecting the scissors-rock-paper event icon, the playable banner is
    # the large lower carousel tile on the right side of the PopKart window.
    x = int(left + width * 0.64)
    y = int(top + height * 0.68)
    print(f"click entry banner fallback: screen=({x},{y})", flush=True)
    move_and_click(x, y)


def choose_response(opponents):
    unique = sorted(set(opponents))
    if len(unique) == 1:
        return WINNING_MOVE[unique[0]]

    candidates = []
    for move in ("jiandao", "shitou", "bu"):
        loses = any(MOVE_BEATS[opp] == move for opp in unique)
        if not loses:
            wins = sum(MOVE_BEATS[move] == opp for opp in unique)
            candidates.append((wins, move))
    if not candidates:
        raise RuntimeError(f"No non-losing move for opponents={opponents}")
    candidates.sort(reverse=True)
    return candidates[0][1]


def detect_opponents(image, expected_count):
    h, w = image.shape[:2]
    # Opponent cards are always in the red-backed area above the VS board.
    region = (0, 0, int(w * 0.78), int(h * 0.36))
    found = []
    for name in ("jiandao", "shitou", "bu"):
        for match in all_matches(image, name, threshold=0.72, region=region, min_distance=60):
            found.append(match)
    found.sort(key=lambda item: item.score, reverse=True)

    chosen = []
    for match in found:
        cx, cy = match.center
        if all((cx - other.center[0]) ** 2 + (cy - other.center[1]) ** 2 >= 70 ** 2 for other in chosen):
            chosen.append(match)
        if len(chosen) >= expected_count:
            break

    if len(chosen) < expected_count:
        details = ", ".join(f"{m.name}:{m.score:.3f}@{m.center}" for m in found[:6])
        raise RuntimeError(f"Expected {expected_count} opponent card(s), got {len(chosen)}. Candidates: {details}")
    chosen.sort(key=lambda item: item.x)
    return [item.name for item in chosen], chosen


def dismiss_after_stage(rect, stage, move):
    end = time.time() + 10
    last_yes = None
    last_no = None
    last_observed_stage = None
    last_won_stages = []
    result_opponent = None
    result_match = None
    result_details = None
    outcome = None

    while time.time() < end:
        image = screenshot_display(rect)
        yes = best_match(image, "yes")
        no = best_match(image, "no")
        if yes.score >= 0.80:
            last_yes = yes
            last_no = no
            try:
                last_observed_stage, stage_match = detect_current_stage(rect, image)
                last_won_stages = detect_won_stages(rect, image)
            except RuntimeError as exc:
                stage_match = None
                print(f"result check: previous={stage} stage/win-detect-pending ({exc})", flush=True)

            try:
                result_opponent, result_match, result_details = detect_result_opponent(rect, image)
                outcome = outcome_for_move(move, result_opponent)
            except RuntimeError as exc:
                print(f"result check: previous={stage} result-card-pending ({exc})", flush=True)

            print(
                f"result check: previous={stage} observed={last_observed_stage} "
                f"wins={last_won_stages} move={move} opponent={result_opponent} "
                f"outcome={outcome} yes={yes.score:.3f} no={no.score:.3f}",
                flush=True,
            )
            if outcome:
                break
        time.sleep(0.2)

    if not last_yes:
        raise TimeoutError(f"Timed out waiting for result dialog after stage {stage}")
    if not outcome:
        raise TimeoutError(f"Timed out detecting result card after stage {stage}")

    print(
        f"stage {stage} result: move={move} opponent={result_opponent} "
        f"outcome={outcome} result-card={result_match.score:.3f}@{result_match.center} "
        f"wins={last_won_stages} candidates=[{result_details}]",
        flush=True,
    )

    if stage == 5 and outcome == "win":
        if not last_no or last_no.score < 0.78:
            raise RuntimeError(f"Stage 5 won, but no button score is too low: {last_no.score if last_no else None}")
        print("stage 5 won: choose no", flush=True)
        click_match(rect, last_no, "no after stage 5 victory")
        time.sleep(1.2)
        wait_and_click_reward_confirm(rect, timeout=15)
        return stage, True

    click_match(rect, last_yes, f"yes after stage {stage} {outcome}")

    try:
        image, observed_stage, stage_match = wait_for_stage(rect, timeout=8)
        won_stages = detect_won_stages(rect, image)
        print(
            f"after confirm: previous={stage} observed={observed_stage} "
            f"stage-row={stage_match.center} wins={won_stages}",
            flush=True,
        )
        return observed_stage, False
    except TimeoutError as exc:
        print(f"after confirm: stage detection timed out ({exc})", flush=True)
        return last_observed_stage or stage, False


def focus_popkart():
    hwnd = win32gui.FindWindow(None, "PopKart Client")
    if hwnd:
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass


def run_once(rect, run_number=1):
    print(f"run {run_number}: start", flush=True)
    focus_popkart()
    time.sleep(0.4)

    image = screenshot_display(rect)
    confirm = find_reward_confirm_button(rect, image)
    if confirm:
        print(f"reward confirm visible at run start: {confirm.center}", flush=True)
        click_match(rect, confirm, "reward confirm at run start")
        time.sleep(2)
        image = screenshot_display(rect)

    try:
        stage, stage_match = detect_current_stage(rect, image)
        print(f"already in challenge: current stage={stage} stage-row={stage_match.center}", flush=True)
    except RuntimeError:
        entry = best_match(image, "entry")
        print(f"entry score={entry.score:.3f} center={entry.center}", flush=True)
        if entry.score >= 0.78:
            click_match(rect, entry, "entry")
            time.sleep(2)

        image, yes = wait_for_match(rect, "yes", threshold=0.80, timeout=12)
        click_match(rect, yes, "initial yes")
        time.sleep(2)

    attempts = 0
    while attempts < 80:
        attempts += 1
        image, stage, stage_match = wait_for_stage(rect, timeout=10)
        print(f"current stage={stage} stage-row={stage_match.center}", flush=True)
        if stage > 5:
            no = best_match(image, "no")
            yes = best_match(image, "yes")
            if no.score >= 0.78 and yes.score >= 0.80:
                print(f"current stage is {stage} with result dialog visible; choose no to stop", flush=True)
                click_match(rect, no, f"no at stage {stage} overshoot")
            else:
                print(f"current stage is {stage}; requested stage 1-5 route is already complete", flush=True)
            break

        expected = 1 if stage <= 2 else 2
        opponents = None
        matches = None
        for attempt in range(20):
            image = screenshot_display(rect)
            try:
                opponents, matches = detect_opponents(image, expected)
                break
            except RuntimeError as exc:
                if attempt == 19:
                    raise
                time.sleep(0.3)

        move = choose_response(opponents)
        printable = ", ".join(f"{m.name}:{m.score:.3f}@{m.center}" for m in matches)
        print(f"stage {stage}: opponents=[{printable}] choose={move}", flush=True)

        user_name = USER_TEMPLATE[move].replace(".png", "")
        user_match = best_match(image, user_name)
        if user_match.score < 0.55:
            raise RuntimeError(f"Could not find user card {user_name}; best score={user_match.score:.3f}")
        click_match(rect, user_match, f"user {move}")
        time.sleep(2)

        _observed_stage, finished = dismiss_after_stage(rect, stage, move)
        time.sleep(2)
        if finished:
            break

    print(f"run {run_number}: done", flush=True)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="repeat runs until stop.loop exists or max-runs is reached")
    parser.add_argument("--max-runs", type=int, default=0, help="maximum loop runs; 0 means unlimited")
    parser.add_argument("--loop-delay", type=float, default=4.0, help="seconds to wait between loop runs")
    return parser.parse_args()


def main():
    args = parse_args()
    set_dpi_awareness()
    rect = find_display_rect()
    print(f"display {DISPLAY_ID}: {rect}", flush=True)

    if STOP_FILE.exists():
        STOP_FILE.unlink()

    run_number = 1
    while True:
        run_once(rect, run_number)
        if not args.loop:
            break
        if args.max_runs and run_number >= args.max_runs:
            print(f"loop: reached max-runs={args.max_runs}", flush=True)
            break
        if STOP_FILE.exists():
            print(f"loop: stop file found at {STOP_FILE}", flush=True)
            break
        run_number += 1
        print(f"loop: waiting {args.loop_delay:.1f}s before run {run_number}", flush=True)
        time.sleep(args.loop_delay)

    print("done", flush=True)


if __name__ == "__main__":
    main()
