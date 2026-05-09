import { createServerFn } from "@tanstack/react-start";

export const generateNiche = createServerFn({ method: "POST" })
  .inputValidator((data: unknown) => {
    const d = data as { description?: string };
    if (!d?.description || typeof d.description !== "string" || d.description.trim().length < 3) {
      throw new Error("Descripción demasiado corta");
    }
    return { description: d.description.trim().slice(0, 500) };
  })
  .handler(async ({ data }) => {
    const apiKey = process.env.LOVABLE_API_KEY;
    if (!apiKey) throw new Error("LOVABLE_API_KEY no configurada");

    const res = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-3-flash-preview",
        messages: [
          {
            role: "system",
            content:
              "Eres un experto GTM. Dado un perfil de cliente ideal, devuelve un nombre de nicho de negocio CORTO (1-3 palabras, en español, capitalizado) y una breve justificación (máx 140 caracteres). Responde SIEMPRE llamando la función create_niche.",
          },
          { role: "user", content: data.description },
        ],
        tools: [
          {
            type: "function",
            function: {
              name: "create_niche",
              description: "Crea un nicho de negocio a partir de la descripción.",
              parameters: {
                type: "object",
                properties: {
                  name: { type: "string", description: "Nombre del nicho, 1-3 palabras en español" },
                  reason: { type: "string", description: "Justificación breve (max 140 chars)" },
                },
                required: ["name", "reason"],
                additionalProperties: false,
              },
            },
          },
        ],
        tool_choice: { type: "function", function: { name: "create_niche" } },
      }),
    });

    if (res.status === 429) throw new Error("Límite de uso alcanzado, intenta más tarde.");
    if (res.status === 402) throw new Error("Sin créditos en Lovable AI. Añade fondos en Workspace > Usage.");
    if (!res.ok) throw new Error(`AI gateway error ${res.status}`);

    const json = await res.json();
    const call = json?.choices?.[0]?.message?.tool_calls?.[0];
    const args = call?.function?.arguments;
    if (!args) throw new Error("Respuesta IA inválida");
    const parsed = JSON.parse(args) as { name: string; reason: string };
    return { name: parsed.name.trim(), reason: parsed.reason.trim() };
  });
