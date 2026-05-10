"""Prompts versionados del sistema (IP del producto)."""
from app.prompts import dia_triple_writer, disector, personaje_builder, safety_filter_llm

PROMPT_VERSIONS = {
    "personaje_builder": personaje_builder.VERSION,
    "dia_triple_writer": dia_triple_writer.VERSION,
    "disector": disector.VERSION,
    "safety_filter_llm": safety_filter_llm.VERSION,
}
