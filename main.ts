// Places the rendered front page where the grader looks for it.
//
// "The World", Tuesday 25 November 2026: the judged artefact is the
// entry.png painted by generate.py (Pillow, no network) from reports
// verified for 24-25 November 2026. Nothing is rendered here — this
// module only carries that finished image into the output directory
// and proves the copy landed whole.

import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

function placeArtwork(): void {
  const scriptDir = dirname(fileURLToPath(import.meta.url));
  const rendered = resolve(scriptDir, "entry.png");

  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  const delivered = resolve(outDir, "entry.png");

  mkdirSync(outDir, { recursive: true });
  copyFileSync(rendered, delivered);

  const sourceBytes = statSync(rendered).size;
  const deliveredBytes = statSync(delivered).size;
  if (deliveredBytes === 0 || deliveredBytes !== sourceBytes) {
    throw new Error(
      `entry.png did not copy cleanly: destination holds ${deliveredBytes} bytes, source holds ${sourceBytes}`,
    );
  }
  console.log(`entry.png -> ${delivered} (${deliveredBytes} bytes)`);
}

placeArtwork();
