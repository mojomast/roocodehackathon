"use client";
import { useEffect } from "react";

export const MswComponent = () => {
  useEffect(() => {
    if (typeof window !== "undefined") {
      if (process.env.NODE_ENV === "development") {
        const { worker } = require("../mocks/browser");
        worker.start();
      }
    }
  }, []);

  return null;
};