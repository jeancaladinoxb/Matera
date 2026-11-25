import type { ReactElement } from "react";

// Ilustraciones planas y originales, una por slug. Solo usan clases que toman su color de los
// tokens (ver plantas.css), así respetan el modo claro y el oscuro.

interface PropsIlustracionPlanta {
  readonly slug?: string;
  readonly className?: string;
}

const HOJA_CORAZON = "M0 0 C-7 -7 -14 3 0 12 C14 3 7 -7 0 0z";

function Maceta() {
  return (
    <>
      <path
        className="plantas-ilu-maceta"
        d="M38 86h44l-4 22a7 7 0 0 1-7 6H49a7 7 0 0 1-7-6z"
      />
      <rect
        className="plantas-ilu-borde"
        height="10"
        rx="5"
        width="54"
        x="33"
        y="78"
      />
    </>
  );
}

function Monstera() {
  return (
    <>
      <path className="plantas-ilu-tallo" d="M58 80 C58 64 52 56 44 46" />
      <path className="plantas-ilu-tallo" d="M62 80 C64 68 72 62 82 56" />
      <path
        className="plantas-ilu-hoja"
        d="M44 48 C28 48 16 36 20 22 C24 10 40 8 48 16 C56 24 54 40 44 48z"
      />
      <path className="plantas-ilu-detalle" d="M21 25 L33 30 M30 12 L36 24 M52 22 L42 28" />
      <path
        className="plantas-ilu-hoja-clara"
        d="M82 58 C68 60 60 48 66 38 C72 28 88 30 94 38 C100 46 96 56 82 58z"
      />
      <path className="plantas-ilu-detalle" d="M68 40 L78 46 M90 33 L84 44" />
      <Maceta />
    </>
  );
}

function Calathea() {
  return (
    <>
      <g transform="rotate(-30 60 80)">
        <ellipse className="plantas-ilu-hoja" cx="60" cy="50" rx="13" ry="30" />
        <path className="plantas-ilu-detalle" d="M60 78 L60 22" />
      </g>
      <g transform="rotate(30 60 80)">
        <ellipse className="plantas-ilu-hoja" cx="60" cy="50" rx="13" ry="30" />
        <path className="plantas-ilu-detalle" d="M60 78 L60 22" />
      </g>
      <g>
        <ellipse className="plantas-ilu-hoja-clara" cx="60" cy="46" rx="14" ry="33" />
        <path className="plantas-ilu-detalle" d="M60 78 L60 16 M60 36 L68 30 M60 50 L52 44 M60 62 L68 56" />
      </g>
      <Maceta />
    </>
  );
}

function Sansevieria() {
  return (
    <>
      <path
        className="plantas-ilu-hoja-clara"
        d="M42 84 C36 66 36 46 40 30 C48 46 54 66 54 84z"
      />
      <path
        className="plantas-ilu-hoja-clara"
        d="M78 84 C84 66 84 46 80 30 C72 46 66 66 66 84z"
      />
      <path
        className="plantas-ilu-hoja"
        d="M50 84 C46 60 50 36 56 14 C62 36 66 60 62 84z"
      />
      <path className="plantas-ilu-detalle" d="M56 80 C54 60 55 40 56 22" />
      <Maceta />
    </>
  );
}

function Pothos() {
  return (
    <>
      <path className="plantas-ilu-tallo" d="M60 80 C44 68 28 74 24 100" />
      <path className="plantas-ilu-tallo" d="M60 80 C76 66 94 74 96 104" />
      <path className="plantas-ilu-tallo" d="M60 80 C58 66 60 54 66 44" />
      <path className="plantas-ilu-hoja" d={HOJA_CORAZON} transform="translate(40 72) rotate(-30)" />
      <path className="plantas-ilu-hoja-clara" d={HOJA_CORAZON} transform="translate(27 88) rotate(-12)" />
      <path className="plantas-ilu-hoja" d={HOJA_CORAZON} transform="translate(80 70) rotate(30)" />
      <path className="plantas-ilu-hoja-clara" d={HOJA_CORAZON} transform="translate(94 90) rotate(14)" />
      <path className="plantas-ilu-hoja" d={HOJA_CORAZON} transform="translate(66 42) rotate(8) scale(1.2)" />
      <Maceta />
    </>
  );
}

function Bonsai() {
  return (
    <>
      <path
        className="plantas-ilu-tronco"
        d="M60 96 C56 84 66 76 58 64 C54 56 60 50 62 44"
      />
      <circle className="plantas-ilu-hoja" cx="44" cy="42" r="16" />
      <circle className="plantas-ilu-hoja" cx="68" cy="34" r="18" />
      <circle className="plantas-ilu-hoja" cx="82" cy="52" r="14" />
      <circle className="plantas-ilu-hoja-clara" cx="62" cy="28" r="8" />
      <circle className="plantas-ilu-hoja-clara" cx="40" cy="38" r="6" />
      <path
        className="plantas-ilu-maceta"
        d="M34 98h52l-3 10a6 6 0 0 1-6 5H43a6 6 0 0 1-6-5z"
      />
      <rect className="plantas-ilu-borde" height="8" rx="4" width="60" x="30" y="92" />
    </>
  );
}

function Generica() {
  return (
    <>
      <path className="plantas-ilu-tallo" d="M60 80 C60 66 60 56 60 46" />
      <path
        className="plantas-ilu-hoja"
        d="M60 52 C44 54 32 44 32 30 C46 28 58 36 60 52z"
      />
      <path
        className="plantas-ilu-hoja-clara"
        d="M60 46 C74 46 86 36 86 22 C72 22 60 30 60 46z"
      />
      <Maceta />
    </>
  );
}

const ILUSTRACIONES: Record<string, () => ReactElement> = {
  monstera: Monstera,
  calathea: Calathea,
  sansevieria: Sansevieria,
  pothos: Pothos,
  bonsai: Bonsai,
};

export function IlustracionPlanta({ slug, className }: PropsIlustracionPlanta) {
  const Dibujo = (slug !== undefined && ILUSTRACIONES[slug]) || Generica;

  return (
    <svg
      aria-hidden="true"
      className={className}
      focusable="false"
      viewBox="0 0 120 120"
    >
      <Dibujo />
    </svg>
  );
}
