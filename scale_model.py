import opensim as osim
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# Update these values for your dataset.
GENERIC_MODEL = "Rajagopal2015_mediapipe.osim"
MARKER_FILE = "E1.trc"
OUTPUT_DIR = "scale_results"

SUBJECT_MASS_KG = 70.0

# Choose a short, quiet segment from the dynamic trial.
TIME_START = 1.20
TIME_END = 1.35


def set_time_range(array_double: osim.ArrayDouble, start_time: float, end_time: float) -> None:
    array_double.setSize(2)
    array_double.set(0, float(start_time))
    array_double.set(1, float(end_time))


def main() -> None:
    if not (BASE_DIR / GENERIC_MODEL).exists():
        raise FileNotFoundError(f"Generic model not found: {BASE_DIR / GENERIC_MODEL}")
    if not (BASE_DIR / MARKER_FILE).exists():
        raise FileNotFoundError(f"Marker file not found: {BASE_DIR / MARKER_FILE}")
    if TIME_END <= TIME_START:
        raise ValueError("TIME_END must be greater than TIME_START")

    (BASE_DIR / OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    output_model = f"{OUTPUT_DIR}/scaled_model.osim"
    output_scale_file = f"{OUTPUT_DIR}/scale_factors.xml"
    output_motion = f"{OUTPUT_DIR}/static_pose.mot"
    output_markers = f"{OUTPUT_DIR}/placed_markers.trc"

    tool = osim.ScaleTool()
    tool.setName("scale_from_python")
    tool.setSubjectMass(SUBJECT_MASS_KG)
    tool.setPathToSubject(str(BASE_DIR) + "/")
    tool.setPrintResultFiles(True)

    tool.getGenericModelMaker().setModelFileName(GENERIC_MODEL)

    model_scaler = tool.getModelScaler()
    model_scaler.setApply(True)
    model_scaler.setMarkerFileName(MARKER_FILE)
    model_scaler.setOutputModelFileName(output_model)
    model_scaler.setOutputScaleFileName(output_scale_file)
    model_scaler.setPrintResultFiles(True)
    set_time_range(model_scaler.getTimeRange(), TIME_START, TIME_END)

    marker_placer = tool.getMarkerPlacer()
    marker_placer.setApply(True)
    marker_placer.setMarkerFileName(MARKER_FILE)
    marker_placer.setOutputModelFileName(output_model)
    marker_placer.setOutputMotionFileName(output_motion)
    marker_placer.setOutputMarkerFileName(output_markers)
    marker_placer.setPrintResultFiles(True)
    marker_placer.setMoveModelMarkers(True)
    set_time_range(marker_placer.getTimeRange(), TIME_START, TIME_END)

    ok = tool.run()
    print(f"ScaleTool success: {ok}")
    print(f"Scaled model: {BASE_DIR / output_model}")


if __name__ == "__main__":
    main()
