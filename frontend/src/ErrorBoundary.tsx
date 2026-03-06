import type { ErrorInfo, ReactNode } from "react";
import { Component } from "react";

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        fetch("http://localhost:8000/error-log", {
            method: "POST",
            body: JSON.stringify({ error: error.message, stack: error.stack }),
            mode: "no-cors"
        }).catch(e => console.log(e));
    }

    public render() {
        if (this.state.hasError) {
            return <h1>Sorry.. there was an error: {this.state.error?.message}</h1>;
        }

        return this.props.children;
    }
}
