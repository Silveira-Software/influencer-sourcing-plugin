# Plugin de Sourcing de Influenciadores para Claude Code

Encontre, pontue e classifique candidatos a influenciadores/criadores do Instagram e TikTok — alimentado por scraping Apify e pontuação Gemini AI.

## O que faz

- **Busca criadores** do TikTok e Instagram por palavras-chave de nicho
- **Pontua com IA** o fit de cada criador com a marca (1-10) usando Gemini
- **Gera DMs de outreach personalizadas** referenciando o conteúdo real de cada criador
- **Exporta para CSV** para sua equipe

## Configuração

### 1. Instale o plugin

```bash
claude --plugin-dir /caminho/para/influencer-sourcing-plugin
```

### 2. Defina variáveis de ambiente

```bash
export APIFY_TOKEN="sua_chave_apify"
export GEMINI_API_KEY="sua_chave_gemini"
```

- Obtenha uma chave Apify em apify.com
- Obtenha uma chave Gemini em aistudio.google.com/apikey

### 3. Instale dependência Python

```bash
pip install requests
```

## Uso

### Sourcing rápido
```
/influencer-sourcing:source-influencers beleza limpa skincare
```

### Pontuar contra um briefing
```
/influencer-sourcing:score-creators MarcaX - suplementos de beleza para mulheres 25-40
```

### Exportar resultados
```
/influencer-sourcing:export-csv
```

### Ou pergunte naturalmente
> "Encontre 20 criadores TikTok no espaço fitness com 50K-500K seguidores e pelo menos 3% de engajamento"

O plugin é acionado automaticamente em solicitações de sourcing de influenciadores.

## Comandos de Barra

| Comando | Descrição |
|---------|-----------|
| `/influencer-sourcing:source-influencers` | Encontre criadores por nicho do IG/TikTok |
| `/influencer-sourcing:score-creators` | Pontue criadores contra um briefing |
| `/influencer-sourcing:export-csv` | Exporte resultados pontuados para CSV |

## Como funciona

1. **Sourcing** — Usa atores Apify para encontrar criadores por nicho
2. **Pontuação** — Envia perfis de criadores para Gemini com contexto do briefing. Gemini pontua o fit de nicho e escreve DMs de outreach personalizadas
3. **Exportação** — Gera um CSV limpo com todos os dados

## Licença

MIT
