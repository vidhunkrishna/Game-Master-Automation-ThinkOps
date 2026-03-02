from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.agents.orchestrator import HeadOrchestratorAgent

orchestrator = HeadOrchestratorAgent()

app = FastAPI(
    title="Multi-Agent Game Master",
    description="Autonomous agent simulation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import world
app.include_router(world.router)


@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Game Master API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "world_state": "/api/world/state",
            "process_tick": "/api/world/tick",
            "all_npcs": "/api/npcs/all",
            "events": "/api/events"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "tick_count": orchestrator.tick_count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
