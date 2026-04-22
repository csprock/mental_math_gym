from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.models import PracticeSession, SessionStatus
from backend.app.deps import get_db
from backend.app.schemas.session import (
    AnswerRequest,
    AnswerResponse,
    AttemptDTO,
    ProblemDTO,
    ProblemDetailDTO,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionDetail,
    SessionListItem,
    SessionSummary,
)
from backend.app.services import session_service as svc

router = APIRouter(prefix="/sessions", tags=["sessions"])

_FINISHED = {SessionStatus.COMPLETED, SessionStatus.ABANDONED}


def _to_list_item(session: PracticeSession) -> SessionListItem:
    return SessionListItem(
        session_id=session.id,
        lesson_id=session.lesson_id,
        status=session.status.value,
        created_at=session.created_at,
        completed_at=session.completed_at,
        total_problems=len(session.problems),
        score=session.score,
        seconds_per_problem=session.seconds_per_problem,
    )


def _to_detail(session: PracticeSession) -> SessionDetail:
    show_answer = session.status in _FINISHED
    summary = svc.compute_summary(session)
    return SessionDetail(
        session_id=session.id,
        lesson_id=session.lesson_id,
        status=session.status.value,
        params=session.params_json or {},
        created_at=session.created_at,
        started_at=session.started_at,
        completed_at=session.completed_at,
        problems=[
            ProblemDetailDTO(
                id=p.id,
                ordinal=p.ordinal,
                prompt=p.prompt,
                answer=p.answer if show_answer else None,
                attempts=[
                    AttemptDTO(
                        id=a.id,
                        attempt_number=a.attempt_number,
                        user_answer=a.user_answer,
                        is_correct=a.is_correct,
                        elapsed_ms=a.elapsed_ms,
                        created_at=a.created_at,
                    )
                    for a in p.attempts
                ],
            )
            for p in session.problems
        ],
        summary=SessionSummary(
            session_id=summary.session_id,
            lesson_id=summary.lesson_id,
            status=summary.status.value,
            total_problems=summary.total_problems,
            correct_problems=summary.correct_problems,
            score=summary.score,
            seconds_per_problem=summary.seconds_per_problem,
            missed_problem_ids=summary.missed_problem_ids,
        ),
    )


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


@router.get("", response_model=list[SessionListItem])
def list_sessions(
    lesson_id: str | None = Query(default=None),
    status: SessionStatus | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[SessionListItem]:
    sessions = svc.list_sessions(
        db, lesson_id=lesson_id, status=status, limit=limit, offset=offset
    )
    return [_to_list_item(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(session_id: int, db: Session = Depends(get_db)) -> SessionDetail:
    try:
        session = svc.get_session_detail(db, session_id)
    except svc.UnknownSessionError:
        raise HTTPException(status_code=404, detail=f"Unknown session: {session_id}")
    return _to_detail(session)


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


@router.post(
    "/{session_id}/retry-missed",
    response_model=SessionCreateResponse,
    status_code=201,
)
def retry_missed(
    session_id: int, db: Session = Depends(get_db)
) -> SessionCreateResponse:
    try:
        new_session = svc.create_retry_session(db, session_id)
    except svc.UnknownSessionError:
        raise HTTPException(status_code=404, detail=f"Unknown session: {session_id}")
    except svc.SessionStateError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return SessionCreateResponse(
        session_id=new_session.id,
        lesson_id=new_session.lesson_id,
        status=new_session.status.value,
        problems=[
            ProblemDTO(id=p.id, ordinal=p.ordinal, prompt=p.prompt)
            for p in new_session.problems
        ],
    )
