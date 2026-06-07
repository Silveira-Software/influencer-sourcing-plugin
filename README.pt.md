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
