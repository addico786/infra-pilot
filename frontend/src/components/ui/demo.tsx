import { DottedSurface } from "./dotted-surface";
import { cn } from "../../lib/utils";

export default function DemoOne() {
  return (
    <DottedSurface className="size-full">
      <div className="dotted-surface-demo">
        <div
          aria-hidden="true"
          className={cn("dotted-surface-demo-glow")}
        />
        <h1 className="dotted-surface-demo-title">Dotted Surface</h1>
      </div>
    </DottedSurface>
  );
}

