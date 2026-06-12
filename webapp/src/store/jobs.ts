import { create } from "zustand";

interface JobsState {
  activeJobId: string | null;
  setActiveJobId: (id: string | null) => void;
}

export const useJobsStore = create<JobsState>((set) => ({
  activeJobId: null,
  setActiveJobId: (id) => set({ activeJobId: id }),
}));
