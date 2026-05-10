// Disclaimer permanente. Se renderiza en cada layout. Es defensa visible
// del principio: el usuario debe saber, en todo momento, que personajes
// y marcas son ficticias.
export function DisclaimerBar() {
  return (
    <div className="disclaimer-bar w-full text-center text-xs py-2 px-4 sticky top-0 z-50">
      <span className="font-medium">Contenido dramatizado</span>
      <span className="opacity-70 mx-2">·</span>
      <span>Personajes y marcas ficticias. Cualquier parecido con la realidad es coincidencia.</span>
    </div>
  );
}
