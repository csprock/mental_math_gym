from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.deps import get_db
from backend.app.schemas.session import (
    AnswerRequest,
    AnswerResponse,
    ProblemDTO,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionSummary,
)
from backend.app.services import session_service as svc

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse, status_code=201)
def create_session(
    req: SessionCreateRequest, db: Session = Depends(get_db)
) -> SessionCreateResponse:
    try:
        session = svc.create_session(
            db, lesson_id=req.lesson_id, size=req.size, params=req.params
        )
    except svc.UnknownLessonError:
        raise HTTPException(status_code=404, detail=f"Unknown lesson: {req.lesson_id!r}")
    except svc.ParamValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return SessionCreateResponse(
        session_id=session.id,
        lesson_id=session.lesson_id,
        status=session.status.value,
        problems=[
            ProblemDTO(id=p.id, ordinal=p.ordinal, prompt=p.prompt)
            for p in session.problems
        ],
    )


@router.post("/{session_id}/answers", response_model=AnswerResponse)
def submit_answer(
    session_id: int, req: AnswerRequest, db: Session = Depends(get_db)
) -> AnswerResponse:
    try:
        result = svc.submit_answer(
            db,
            session_id=session_id,
            problem_id=req.problem_id,
            user_answer=req.user_answer,
            elapsed_ms=req.elapsed_ms,
        )
    except svc.UnknownSessionError:
        raise HTTPException(status_code=404, detail=f"Unknown session: {session_id}")
    except svc.UnknownProblemError:
        raise HTTPException(
            status_code=404,
            detail=f"Problem {req.problem_id} not in session {session_id}",
        )
    except svc.SessionStateError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return AnswerResponse(
        correct=result.attempt.is_correct,
        correct_answer=result.correct_answer,
        attempt_number=result.attempt.attempt_number,
    )


@router.post("/{session_id}/complete", response_model=SessionSummary)
def complete_session(session_id: int, db: Session = Depends(get_db)) -> SessionSummary:
    try:
        summary = svc.complete_session(db, session_id)
    except svc.UnknownSessionError:
        raise HTTPException(status_code=404, detail=f"Unknown session: {session_id}")

    return SessionSummary(
        session_id=summary.session_id,
        lesson_id=summary.lesson_id,
        status=summary.status.value,
        total_problems=summary.total_problems,
        correct_problems=summary.correct_problems,
        score=summary.score,
        seconds_per_problem=summary.seconds_per_problem,
        missed_problem_ids=summary.missed_problem_ids,
    )
