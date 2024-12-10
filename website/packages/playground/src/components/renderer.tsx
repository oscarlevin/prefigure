import React from "react";
import { useStoreActions, useStoreState } from "../state";
import {
    Button,
    ButtonGroup,
    Nav,
    Spinner,
    ToggleButton,
} from "react-bootstrap";
import { Download } from "react-bootstrap-icons";

/**
 * Renders and displays the currently active PreFigure source code.
 */
export function Renderer() {
    const loadPyodide = useStoreActions((actions) => actions.loadPyodide);
    const status = useStoreState((state) => state.status);
    const compiledSource = useStoreState((state) => state.compiledSource);
    const compile = useStoreActions((actions) => actions.compile);
    const mode = useStoreState((state) => state.compileMode);
    const setMode = useStoreActions((actions) => actions.setCompileMode);

    React.useEffect(() => {
        loadPyodide();
    }, []);

    if (status === "loadingPyodide") {
        return (
            <div className="loading">
                <Spinner animation="border" style={{ marginRight: "5px" }} />{" "}
                Loading Pyodide...
            </div>
        );
    }

    return (
        <div className="render-frame">
            <div className="render-content">
                {compiledSource.startsWith("<svg") ? (
                    <div
                        className="rendered-svg"
                        dangerouslySetInnerHTML={{ __html: compiledSource }}
                    ></div>
                ) : (
                    compiledSource
                )}
            </div>
            <Nav>
                <Button variant="success" onClick={() => compile()}>
                    Compile
                </Button>
                Render mode:{" "}
                <ButtonGroup>
                    <ToggleButton
                        id="toggle-visual"
                        value={1}
                        checked={mode === "svg"}
                        active={mode === "svg"}
                        variant={mode === "svg" ? "primary" : "outline-secondary"}
                        onClick={() => setMode("svg")}
                    >
                        Visual
                    </ToggleButton>
                    <ToggleButton
                        id="toggle-visual"
                        value={2}
                        checked={mode === "tactile"}
                        active={mode === "tactile"}
                        variant={mode === "tactile" ? "primary" : "outline-secondary"}
                        onClick={() => setMode("tactile")}
                    >
                        Tactile
                    </ToggleButton>
                </ButtonGroup>
                <Button size="sm">
                    <Download /> Download
                </Button>
            </Nav>
        </div>
    );
}
