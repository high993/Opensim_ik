import opensim as osim
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SCALED_MODEL = BASE_DIR / "scale_results" / "scaled_model.osim"
MARKER_FILE = BASE_DIR / "E1.trc"
OUTPUT_DIR = BASE_DIR / "ik_results"
OUTPUT_MOTION = OUTPUT_DIR / "ik.mot"

START_TIME = None
END_TIME = None
MARKER_WEIGHT = 1.0
ACCURACY = 1e-5
CONSTRAINT_WEIGHT = float("inf")
REPORT_MARKER_LOCATIONS = True


def read_trc_marker_names(trc_path: Path) -> list[str]:
    lines = trc_path.read_text().splitlines()
    if len(lines) < 4:
        raise ValueError(f"TRC file is too short: {trc_path}")
    header = lines[3].strip().split()
    return header[2:]


def read_trc_time_range(trc_path: Path) -> tuple[float, float]:
    lines = trc_path.read_text().splitlines()[5:]
    times = [float(line.split()[1]) for line in lines if line.strip()]
    if not times:
        raise ValueError(f"No frame data found in TRC file: {trc_path}")
    return times[0], times[-1]


def build_marker_tasks(tool: osim.InverseKinematicsTool, model: osim.Model, marker_names: list[str]) -> list[str]:
    trc_markers = set(marker_names)
    task_set = tool.upd_IKTaskSet()
    matched = []

    model_markers = model.getMarkerSet()
    for i in range(model_markers.getSize()):
        name = model_markers.get(i).getName()
        if name not in trc_markers:
            continue
        task = osim.IKMarkerTask()
        task.setName(name)
        task.setApply(True)
        task.setWeight(MARKER_WEIGHT)
        task_set.adoptAndAppend(task)
        matched.append(name)

    if not matched:
        raise RuntimeError("No overlapping marker names found between model and TRC file.")

    return matched


def main() -> None:
    if not SCALED_MODEL.exists():
        raise FileNotFoundError(f"Scaled model not found: {SCALED_MODEL}")
    if not MARKER_FILE.exists():
        raise FileNotFoundError(f"Marker file not found: {MARKER_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    trc_start, trc_end = read_trc_time_range(MARKER_FILE)
    start_time = trc_start if START_TIME is None else float(START_TIME)
    end_time = trc_end if END_TIME is None else float(END_TIME)

    if end_time <= start_time:
        raise ValueError("END_TIME must be greater than START_TIME")

    model = osim.Model(str(SCALED_MODEL))
    marker_names = read_trc_marker_names(MARKER_FILE)

    tool = osim.InverseKinematicsTool()
    tool.setModel(model)
    tool.setMarkerDataFileName(str(MARKER_FILE))
    tool.setStartTime(start_time)
    tool.setEndTime(end_time)
    tool.setOutputMotionFileName(str(OUTPUT_MOTION))
    tool.setResultsDir(str(OUTPUT_DIR))
    tool.set_accuracy(ACCURACY)
    tool.set_constraint_weight(CONSTRAINT_WEIGHT)
    tool.set_report_marker_locations(REPORT_MARKER_LOCATIONS)

    matched = build_marker_tasks(tool, model, marker_names)

    print(f"Running IK from {start_time:.6f} to {end_time:.6f} s")
    print(f"Using {len(matched)} markers: {', '.join(matched)}")

    ok = tool.run()
    print(f"InverseKinematicsTool success: {ok}")
    print(f"Output motion: {OUTPUT_MOTION}")


if __name__ == "__main__":
    main()
