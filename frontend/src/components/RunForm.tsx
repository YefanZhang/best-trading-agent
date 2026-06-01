import { Play } from "lucide-react";
import { type FormEvent, useState } from "react";

type RunFormProps = {
  disabled: boolean;
  onSubmit: (ticker: string) => void;
};

export function RunForm({ disabled, onSubmit }: RunFormProps) {
  const [ticker, setTicker] = useState("NVDA");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(ticker);
  }

  return (
    <form className="run-form" onSubmit={handleSubmit}>
      <label>
        Ticker
        <input value={ticker} onChange={(event) => setTicker(event.target.value)} />
      </label>
      <button className="primary-button" disabled={disabled} type="submit">
        <Play size={18} strokeWidth={2.2} aria-hidden="true" />
        Start research
      </button>
    </form>
  );
}
