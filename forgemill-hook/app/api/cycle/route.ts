import { NextResponse } from "next/server";

const NTFY = "https://ntfy.sh/btp-forgemill-raj-integrity";

let last = { running: false, reason: "idle", t: 0 };

export async function GET() {
  return NextResponse.json(last, {
    headers: { "Access-Control-Allow-Origin": "*" },
  });
}

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  last = {
    running: Boolean(body.running),
    reason: String(body.reason || ""),
    t: Date.now(),
  };
  try {
    await fetch(NTFY, { method: "POST", body: last.running ? "start" : "stop" });
  } catch {
    /* ntfy is the durable cross-laptop signal */
  }
  return NextResponse.json(last, {
    headers: { "Access-Control-Allow-Origin": "*" },
  });
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
