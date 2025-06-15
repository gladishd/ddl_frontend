import { NextResponse } from "next/server";
import { listDocuments } from "@/lib/db";

export async function GET() {
  const docs = await listDocuments();
  return NextResponse.json(docs);
}