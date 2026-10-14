import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.config import settings
from backend.app.models.schemas import (
    Asset,
    AssetCreate,
    BoundingBox,
    CaptureViewEnum,
    ChangeProposal,
    ConditionTypeEnum,
    Inspection,
    InspectionCreate,
    InspectionStatusEnum,
    KitItem,
    MediaEvidence,
    ProposalDecisionEnum,
    SeverityEnum,
)
from backend.app.services.fixture_generator import ensure_fixture_images
from backend.app.services.storage import (
    calculate_sha256,
    ensure_upload_dirs,
    get_public_url,
    save_crop_image,
)


class Repository:
    """Production-grade SQLite persistence layer with ACID transactions."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            raw_url = settings.DATABASE_URL
            if raw_url.startswith("sqlite:///"):
                db_path = raw_url[len("sqlite:///") :]
            else:
                db_path = "gearwitness.db"

        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        """Creates tables if not present and performs idempotent seeding."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    serial_number TEXT NOT NULL,
                    qr_code TEXT,
                    kit_items_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS inspections (
                    id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    asset_name TEXT NOT NULL,
                    serial_number TEXT NOT NULL,
                    customer_reference TEXT NOT NULL,
                    status TEXT NOT NULL,
                    checkout_timestamp TEXT,
                    checkin_timestamp TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS media (
                    id TEXT PRIMARY KEY,
                    inspection_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    public_url TEXT NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    file_size_bytes INTEGER NOT NULL,
                    mime_type TEXT NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    capture_view TEXT NOT NULL,
                    captured_at TEXT NOT NULL,
                    is_checkout INTEGER NOT NULL,
                    FOREIGN KEY (inspection_id) REFERENCES inspections (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY,
                    inspection_id TEXT NOT NULL,
                    capture_view TEXT NOT NULL,
                    bbox_x REAL NOT NULL,
                    bbox_y REAL NOT NULL,
                    bbox_w REAL NOT NULL,
                    bbox_h REAL NOT NULL,
                    checkout_crop_path TEXT,
                    checkin_crop_path TEXT,
                    checkout_crop_url TEXT,
                    checkin_crop_url TEXT,
                    condition_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT NOT NULL,
                    model_rationale TEXT NOT NULL,
                    operator_decision TEXT NOT NULL,
                    operator_notes TEXT,
                    resolved_at TEXT,
                    FOREIGN KEY (inspection_id) REFERENCES inspections (id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS kit_items (
                    id TEXT NOT NULL,
                    inspection_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    description TEXT,
                    is_present_checkout INTEGER NOT NULL,
                    is_present_checkin INTEGER,
                    serial_or_part_no TEXT,
                    PRIMARY KEY (inspection_id, id),
                    FOREIGN KEY (inspection_id) REFERENCES inspections (id) ON DELETE CASCADE
                );
                """
            )

            # Check if inspections table is empty
            cur = conn.cursor()
            cur.execute("SELECT count(*) as count FROM inspections")
            row = cur.fetchone()
            if row["count"] == 0:
                self._seed_default_data(conn)

    def _seed_default_data(self, conn: sqlite3.Connection):
        """Initializes default asset catalog and preloaded hero demo inspection."""
        ensure_upload_dirs()
        fixture_paths = ensure_fixture_images()

        # Asset 1: Sony FX3 Cinema Kit
        fx3_id = "asset_fx3_cinema"
        kit_items = [
            KitItem(
                id="kit_01",
                name="Sony FX3 Camera Body",
                quantity=1,
                serial_or_part_no="S/N 4892011",
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="kit_02",
                name="FE 24-70mm f/2.8 GM Lens",
                quantity=1,
                serial_or_part_no="S/N 1928374",
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="kit_03",
                name="Dual Fast Battery Charger",
                quantity=1,
                serial_or_part_no="BC-QZ1",
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="kit_04",
                name="USB-C 10Gbps Tether Cable",
                quantity=1,
                serial_or_part_no="CAB-TC10",
                is_present_checkout=True,
                is_present_checkin=False,  # Intentionally missing in demo
            ),
            KitItem(
                id="kit_05",
                name="Pelican 1510 Hardcase",
                quantity=1,
                serial_or_part_no="PEL-1510-BK",
                is_present_checkout=True,
                is_present_checkin=True,
            ),
        ]

        fx3_asset = Asset(
            id=fx3_id,
            name="Sony FX3 Cinema Kit",
            category="Cinema Cameras",
            serial_number="4892011",
            qr_code="QR-FX3-4892011",
            kit_items=kit_items,
        )

        conn.execute(
            """
            INSERT INTO assets (id, name, category, serial_number, qr_code, kit_items_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fx3_asset.id,
                fx3_asset.name,
                fx3_asset.category,
                fx3_asset.serial_number,
                fx3_asset.qr_code,
                json.dumps([item.model_dump() for item in kit_items]),
                fx3_asset.created_at.isoformat(),
            ),
        )

        # Asset 2: DeWalt Drill Kit
        dewalt_asset = Asset(
            id="asset_dewalt_drill",
            name="DeWalt 20V MAX XR Hammer Drill Kit",
            category="Power Tools",
            serial_number="DW-883920",
            qr_code="QR-DW-883920",
            kit_items=[
                KitItem(
                    id="kit_dw_01",
                    name="DCD996 Hammerdrill Tool",
                    quantity=1,
                    serial_or_part_no="DCD996",
                    is_present_checkout=True,
                    is_present_checkin=True,
                ),
                KitItem(
                    id="kit_dw_02",
                    name="5.0Ah XR Battery Pack",
                    quantity=2,
                    serial_or_part_no="DCB205",
                    is_present_checkout=True,
                    is_present_checkin=True,
                ),
            ],
        )

        conn.execute(
            """
            INSERT INTO assets (id, name, category, serial_number, qr_code, kit_items_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dewalt_asset.id,
                dewalt_asset.name,
                dewalt_asset.category,
                dewalt_asset.serial_number,
                dewalt_asset.qr_code,
                json.dumps([item.model_dump() for item in dewalt_asset.kit_items]),
                dewalt_asset.created_at.isoformat(),
            ),
        )

        # Hero Inspection: insp_hero_demo
        hero_id = "insp_hero_demo"
        t_checkout = datetime(2026, 10, 10, 9, 30, tzinfo=timezone.utc)
        t_checkin = datetime(2026, 10, 14, 16, 45, tzinfo=timezone.utc)

        conn.execute(
            """
            INSERT INTO inspections (
                id, asset_id, asset_name, serial_number, customer_reference,
                status, checkout_timestamp, checkin_timestamp, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hero_id,
                fx3_id,
                fx3_asset.name,
                fx3_asset.serial_number,
                "CUST-7749-BERLIN",
                InspectionStatusEnum.REVIEW_READY.value,
                t_checkout.isoformat(),
                t_checkin.isoformat(),
                "4-day commercial shoot return. Exterior inspection completed.",
                t_checkout.isoformat(),
                t_checkin.isoformat(),
            ),
        )

        # Media items
        media_specs = [
            ("med_front_co", fixture_paths["front_checkout"], CaptureViewEnum.FRONT, True),
            ("med_front_ci", fixture_paths["front_checkin"], CaptureViewEnum.FRONT, False),
            (
                "med_acc_co",
                fixture_paths["accessories_checkout"],
                CaptureViewEnum.ACCESSORIES,
                True,
            ),
            (
                "med_acc_ci",
                fixture_paths["accessories_checkin"],
                CaptureViewEnum.ACCESSORIES,
                False,
            ),
        ]

        for m_id, f_path, c_view, is_co in media_specs:
            file_bytes = b""
            if os.path.exists(f_path):
                with open(f_path, "rb") as bf:
                    file_bytes = bf.read()
            m_hash = calculate_sha256(file_bytes) if file_bytes else "demo_hash"
            pub_url = get_public_url(f_path) or f"/{f_path}"

            conn.execute(
                """
                INSERT INTO media (
                    id, inspection_id, filename, storage_path, public_url, sha256_hash,
                    file_size_bytes, mime_type, width, height, capture_view, captured_at, is_checkout
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    m_id,
                    hero_id,
                    os.path.basename(f_path),
                    f_path,
                    pub_url,
                    m_hash,
                    len(file_bytes),
                    "image/jpeg",
                    640,
                    480,
                    c_view.value,
                    t_checkout.isoformat() if is_co else t_checkin.isoformat(),
                    1 if is_co else 0,
                ),
            )

        # Generate real crops for demo proposals
        bbox1 = BoundingBox(x=0.55, y=0.48, width=0.15, height=0.10)
        crop1_path, crop1_url = save_crop_image(
            fixture_paths["front_checkin"], bbox1, "crop_scratch_front"
        )
        crop1_co_path, crop1_co_url = save_crop_image(
            fixture_paths["front_checkout"], bbox1, "crop_base_front"
        )

        bbox2 = BoundingBox(x=0.32, y=0.40, width=0.10, height=0.10)
        crop2_path, crop2_url = save_crop_image(
            fixture_paths["front_checkin"], bbox2, "crop_glare_front"
        )
        crop2_co_path, crop2_co_url = save_crop_image(
            fixture_paths["front_checkout"], bbox2, "crop_glare_base"
        )

        bbox3 = BoundingBox(x=0.70, y=0.53, width=0.12, height=0.20)
        crop3_path, crop3_url = save_crop_image(
            fixture_paths["accessories_checkin"], bbox3, "crop_cable_acc"
        )
        crop3_co_path, crop3_co_url = save_crop_image(
            fixture_paths["accessories_checkout"], bbox3, "crop_cable_base"
        )

        # Proposals (including prop_01_scratch and prop_01 for backward compatibility)
        proposals_data = [
            (
                "prop_01_scratch",
                hero_id,
                CaptureViewEnum.FRONT.value,
                bbox1.x,
                bbox1.y,
                bbox1.width,
                bbox1.height,
                crop1_co_path,
                crop1_path,
                crop1_co_url,
                crop1_url,
                ConditionTypeEnum.SCRATCH.value,
                SeverityEnum.MINOR.value,
                0.89,
                "Fresh scratch on front command dial housing.",
                "Luminance gradient and edge disruption indicates a 4mm scratch breaching the anodized coating. Not present in checkout baseline.",
                ProposalDecisionEnum.PENDING.value,
                None,
                None,
            ),
            (
                "prop_02_glare",
                hero_id,
                CaptureViewEnum.FRONT.value,
                bbox2.x,
                bbox2.y,
                bbox2.width,
                bbox2.height,
                crop2_co_path,
                crop2_path,
                crop2_co_url,
                crop2_url,
                ConditionTypeEnum.ARTIFACT_LIGHTING.value,
                SeverityEnum.NONE.value,
                0.82,
                "Specular highlight reflection on sensor glass.",
                "Diff heatmap shows localized luminescence peak. Consistent with 45° overhead counter lighting; no scratch or coating abrasion detected.",
                ProposalDecisionEnum.PENDING.value,
                None,
                None,
            ),
            (
                "prop_03_cable",
                hero_id,
                CaptureViewEnum.ACCESSORIES.value,
                bbox3.x,
                bbox3.y,
                bbox3.width,
                bbox3.height,
                crop3_co_path,
                crop3_path,
                crop3_co_url,
                crop3_url,
                ConditionTypeEnum.MISSING_ACCESSORY.value,
                SeverityEnum.MODERATE.value,
                0.95,
                "USB-C 10Gbps tethering cable missing from compartment 4.",
                "Foam insert compartment 4 is empty in return check-in image. Verified present at checkout.",
                ProposalDecisionEnum.PENDING.value,
                None,
                None,
            ),
        ]

        conn.executemany(
            """
            INSERT INTO proposals (
                id, inspection_id, capture_view, bbox_x, bbox_y, bbox_w, bbox_h,
                checkout_crop_path, checkin_crop_path, checkout_crop_url, checkin_crop_url,
                condition_type, severity, confidence, description, model_rationale,
                operator_decision, operator_notes, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            proposals_data,
        )

        # Kit items
        kit_rows = [
            (
                item.id,
                hero_id,
                item.name,
                item.quantity,
                item.description,
                1 if item.is_present_checkout else 0,
                None if item.is_present_checkin is None else (1 if item.is_present_checkin else 0),
                item.serial_or_part_no,
            )
            for item in kit_items
        ]

        conn.executemany(
            """
            INSERT INTO kit_items (
                id, inspection_id, name, quantity, description,
                is_present_checkout, is_present_checkin, serial_or_part_no
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            kit_rows,
        )

    # -------------------------------------------------------------------------
    # Asset Operations
    # -------------------------------------------------------------------------
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
            row = cur.fetchone()
            if not row:
                return None
            kit_items = [KitItem(**k) for k in json.loads(row["kit_items_json"])]
            return Asset(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                serial_number=row["serial_number"],
                qr_code=row["qr_code"],
                kit_items=kit_items,
                created_at=datetime.fromisoformat(row["created_at"]),
            )

    def list_assets(self) -> List[Asset]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM assets ORDER BY created_at DESC")
            assets = []
            for row in cur.fetchall():
                kit_items = [KitItem(**k) for k in json.loads(row["kit_items_json"])]
                assets.append(
                    Asset(
                        id=row["id"],
                        name=row["name"],
                        category=row["category"],
                        serial_number=row["serial_number"],
                        qr_code=row["qr_code"],
                        kit_items=kit_items,
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
                )
            return assets

    def create_asset(self, asset_in: AssetCreate) -> Asset:
        asset_id = f"asset_{uuid.uuid4().hex[:8]}"
        kit_items = [
            KitItem(
                id=f"kit_{i+1:02d}",
                name=k.name,
                quantity=k.quantity,
                description=k.description,
                serial_or_part_no=k.serial_or_part_no,
            )
            for i, k in enumerate(asset_in.kit_items)
        ]

        now = datetime.now(timezone.utc)
        asset = Asset(
            id=asset_id,
            name=asset_in.name,
            category=asset_in.category,
            serial_number=asset_in.serial_number,
            qr_code=asset_in.qr_code,
            kit_items=kit_items,
            created_at=now,
        )

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO assets (id, name, category, serial_number, qr_code, kit_items_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    asset.id,
                    asset.name,
                    asset.category,
                    asset.serial_number,
                    asset.qr_code,
                    json.dumps([item.model_dump() for item in kit_items]),
                    now.isoformat(),
                ),
            )
        return asset

    # -------------------------------------------------------------------------
    # Inspection Operations
    # -------------------------------------------------------------------------
    def get_inspection(self, inspection_id: str) -> Optional[Inspection]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,))
            i_row = cur.fetchone()
            if not i_row:
                return None

            # Fetch media
            cur.execute(
                "SELECT * FROM media WHERE inspection_id = ? ORDER BY captured_at ASC",
                (inspection_id,),
            )
            media = [
                MediaEvidence(
                    id=m["id"],
                    filename=m["filename"],
                    storage_path=m["storage_path"],
                    public_url=m["public_url"],
                    sha256_hash=m["sha256_hash"],
                    file_size_bytes=m["file_size_bytes"],
                    mime_type=m["mime_type"],
                    width=m["width"],
                    height=m["height"],
                    capture_view=CaptureViewEnum(m["capture_view"]),
                    captured_at=datetime.fromisoformat(m["captured_at"]),
                    is_checkout=bool(m["is_checkout"]),
                )
                for m in cur.fetchall()
            ]

            # Fetch proposals
            cur.execute("SELECT * FROM proposals WHERE inspection_id = ?", (inspection_id,))
            proposals = [
                ChangeProposal(
                    id=p["id"],
                    inspection_id=p["inspection_id"],
                    capture_view=CaptureViewEnum(p["capture_view"]),
                    bounding_box=BoundingBox(
                        x=p["bbox_x"],
                        y=p["bbox_y"],
                        width=p["bbox_w"],
                        height=p["bbox_h"],
                    ),
                    checkout_crop_path=p["checkout_crop_path"],
                    checkin_crop_path=p["checkin_crop_path"],
                    checkout_crop_url=p["checkout_crop_url"]
                    or get_public_url(p["checkout_crop_path"]),
                    checkin_crop_url=p["checkin_crop_url"]
                    or get_public_url(p["checkin_crop_path"]),
                    condition_type=ConditionTypeEnum(p["condition_type"]),
                    severity=SeverityEnum(p["severity"]),
                    confidence=p["confidence"],
                    description=p["description"],
                    model_rationale=p["model_rationale"],
                    operator_decision=ProposalDecisionEnum(p["operator_decision"]),
                    operator_notes=p["operator_notes"],
                    resolved_at=(
                        datetime.fromisoformat(p["resolved_at"]) if p["resolved_at"] else None
                    ),
                )
                for p in cur.fetchall()
            ]

            # Fetch kit checklist
            cur.execute("SELECT * FROM kit_items WHERE inspection_id = ?", (inspection_id,))
            kit_checklist = [
                KitItem(
                    id=k["id"],
                    name=k["name"],
                    quantity=k["quantity"],
                    description=k["description"],
                    is_present_checkout=bool(k["is_present_checkout"]),
                    is_present_checkin=(
                        bool(k["is_present_checkin"])
                        if k["is_present_checkin"] is not None
                        else None
                    ),
                    serial_or_part_no=k["serial_or_part_no"],
                )
                for k in cur.fetchall()
            ]

            return Inspection(
                id=i_row["id"],
                asset_id=i_row["asset_id"],
                asset_name=i_row["asset_name"],
                serial_number=i_row["serial_number"],
                customer_reference=i_row["customer_reference"],
                status=InspectionStatusEnum(i_row["status"]),
                checkout_timestamp=(
                    datetime.fromisoformat(i_row["checkout_timestamp"])
                    if i_row["checkout_timestamp"]
                    else None
                ),
                checkin_timestamp=(
                    datetime.fromisoformat(i_row["checkin_timestamp"])
                    if i_row["checkin_timestamp"]
                    else None
                ),
                media=media,
                proposals=proposals,
                kit_checklist=kit_checklist,
                notes=i_row["notes"],
                created_at=datetime.fromisoformat(i_row["created_at"]),
                updated_at=datetime.fromisoformat(i_row["updated_at"]),
            )

    def list_inspections(self) -> List[Inspection]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM inspections ORDER BY updated_at DESC")
            ids = [r["id"] for r in cur.fetchall()]
        return [self.get_inspection(iid) for iid in ids if iid]

    def create_inspection(self, insp_in: InspectionCreate) -> Inspection:
        asset = self.get_asset(insp_in.asset_id)
        if not asset:
            raise ValueError(f"Asset '{insp_in.asset_id}' not found.")

        insp_id = f"insp_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        kit_checklist = [
            KitItem(
                id=item.id,
                name=item.name,
                quantity=item.quantity,
                description=item.description,
                is_present_checkout=True,
                is_present_checkin=None,
                serial_or_part_no=item.serial_or_part_no,
            )
            for item in asset.kit_items
        ]

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO inspections (
                    id, asset_id, asset_name, serial_number, customer_reference,
                    status, checkout_timestamp, checkin_timestamp, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    insp_id,
                    asset.id,
                    asset.name,
                    asset.serial_number,
                    insp_in.customer_reference,
                    InspectionStatusEnum.CREATED.value,
                    now.isoformat(),
                    None,
                    insp_in.notes,
                    now.isoformat(),
                    now.isoformat(),
                ),
            )

            kit_rows = [
                (
                    item.id,
                    insp_id,
                    item.name,
                    item.quantity,
                    item.description,
                    1,
                    None,
                    item.serial_or_part_no,
                )
                for item in kit_checklist
            ]
            conn.executemany(
                """
                INSERT INTO kit_items (
                    id, inspection_id, name, quantity, description,
                    is_present_checkout, is_present_checkin, serial_or_part_no
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                kit_rows,
            )

        return self.get_inspection(insp_id)

    def update_inspection(self, inspection: Inspection) -> Inspection:
        now = datetime.now(timezone.utc)
        inspection.updated_at = now
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE inspections SET
                    status = ?,
                    checkout_timestamp = ?,
                    checkin_timestamp = ?,
                    notes = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    inspection.status.value,
                    (
                        inspection.checkout_timestamp.isoformat()
                        if inspection.checkout_timestamp
                        else None
                    ),
                    (
                        inspection.checkin_timestamp.isoformat()
                        if inspection.checkin_timestamp
                        else None
                    ),
                    inspection.notes,
                    now.isoformat(),
                    inspection.id,
                ),
            )
        return self.get_inspection(inspection.id)

    def add_media_to_inspection(
        self, inspection_id: str, media: MediaEvidence
    ) -> Optional[Inspection]:
        inspection = self.get_inspection(inspection_id)
        if not inspection:
            return None

        now = datetime.now(timezone.utc)
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO media (
                    id, inspection_id, filename, storage_path, public_url, sha256_hash,
                    file_size_bytes, mime_type, width, height, capture_view, captured_at, is_checkout
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    media.id,
                    inspection_id,
                    media.filename,
                    media.storage_path,
                    media.public_url,
                    media.sha256_hash,
                    media.file_size_bytes,
                    media.mime_type,
                    media.width,
                    media.height,
                    media.capture_view.value,
                    media.captured_at.isoformat(),
                    1 if media.is_checkout else 0,
                ),
            )

            # Update inspection status if needed
            new_status = inspection.status.value
            if media.is_checkout and inspection.status == InspectionStatusEnum.CREATED:
                new_status = InspectionStatusEnum.CHECKOUT_CAPTURED.value
            elif (
                not media.is_checkout
                and inspection.status == InspectionStatusEnum.CHECKOUT_CAPTURED
            ):
                new_status = InspectionStatusEnum.CHECKIN_CAPTURED.value

            conn.execute(
                "UPDATE inspections SET status = ?, updated_at = ? WHERE id = ?",
                (new_status, now.isoformat(), inspection_id),
            )

        return self.get_inspection(inspection_id)

    def update_proposal_decision(
        self,
        inspection_id: str,
        proposal_id: str,
        decision: ProposalDecisionEnum,
        notes: Optional[str] = None,
    ) -> Optional[Inspection]:
        now = datetime.now(timezone.utc)
        resolved_at = now.isoformat() if decision != ProposalDecisionEnum.PENDING else None

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE proposals SET
                    operator_decision = ?,
                    operator_notes = COALESCE(?, operator_notes),
                    resolved_at = ?
                WHERE id = ? AND inspection_id = ?
                """,
                (decision.value, notes, resolved_at, proposal_id, inspection_id),
            )
            if cur.rowcount == 0:
                return None

            conn.execute(
                "UPDATE inspections SET updated_at = ? WHERE id = ?",
                (now.isoformat(), inspection_id),
            )

        return self.get_inspection(inspection_id)

    def get_proposal(
        self, inspection_id: str, proposal_id: str
    ) -> Optional[ChangeProposal]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM proposals WHERE id = ? AND inspection_id = ?",
                (proposal_id, inspection_id),
            )
            p = cur.fetchone()
            if not p:
                return None
            return ChangeProposal(
                id=p["id"],
                inspection_id=p["inspection_id"],
                capture_view=CaptureViewEnum(p["capture_view"]),
                bounding_box=BoundingBox(
                    x=p["bbox_x"],
                    y=p["bbox_y"],
                    width=p["bbox_w"],
                    height=p["bbox_h"],
                ),
                checkout_crop_path=p["checkout_crop_path"],
                checkin_crop_path=p["checkin_crop_path"],
                checkout_crop_url=p["checkout_crop_url"]
                or get_public_url(p["checkout_crop_path"]),
                checkin_crop_url=p["checkin_crop_url"]
                or get_public_url(p["checkin_crop_path"]),
                condition_type=ConditionTypeEnum(p["condition_type"]),
                severity=SeverityEnum(p["severity"]),
                confidence=p["confidence"],
                description=p["description"],
                model_rationale=p["model_rationale"],
                operator_decision=ProposalDecisionEnum(p["operator_decision"]),
                operator_notes=p["operator_notes"],
                resolved_at=(
                    datetime.fromisoformat(p["resolved_at"]) if p["resolved_at"] else None
                ),
            )

    def get_kit_item(
        self, inspection_id: str, item_id: str
    ) -> Optional[KitItem]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM kit_items WHERE id = ? AND inspection_id = ?",
                (item_id, inspection_id),
            )
            k = cur.fetchone()
            if not k:
                return None
            return KitItem(
                id=k["id"],
                name=k["name"],
                quantity=k["quantity"],
                description=k["description"],
                is_present_checkout=bool(k["is_present_checkout"]),
                is_present_checkin=(
                    bool(k["is_present_checkin"])
                    if k["is_present_checkin"] is not None
                    else None
                ),
                serial_or_part_no=k["serial_or_part_no"],
            )

    def update_kit_item_status(
        self, inspection_id: str, item_id: str, is_present: bool
    ) -> Optional[Inspection]:
        now = datetime.now(timezone.utc)
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE kit_items SET
                    is_present_checkin = ?
                WHERE id = ? AND inspection_id = ?
                """,
                (1 if is_present else 0, item_id, inspection_id),
            )
            if cur.rowcount == 0:
                return None

            conn.execute(
                "UPDATE inspections SET updated_at = ? WHERE id = ?",
                (now.isoformat(), inspection_id),
            )

        return self.get_inspection(inspection_id)

    def set_inspection_proposals(
        self, inspection_id: str, proposals: List[ChangeProposal]
    ) -> Optional[Inspection]:
        now = datetime.now(timezone.utc)
        with self._get_connection() as conn:
            conn.execute("DELETE FROM proposals WHERE inspection_id = ?", (inspection_id,))
            rows = [
                (
                    p.id,
                    inspection_id,
                    p.capture_view.value,
                    p.bounding_box.x,
                    p.bounding_box.y,
                    p.bounding_box.width,
                    p.bounding_box.height,
                    p.checkout_crop_path,
                    p.checkin_crop_path,
                    p.checkout_crop_url or get_public_url(p.checkout_crop_path),
                    p.checkin_crop_url or get_public_url(p.checkin_crop_path),
                    p.condition_type.value,
                    p.severity.value,
                    p.confidence,
                    p.description,
                    p.model_rationale,
                    p.operator_decision.value,
                    p.operator_notes,
                    p.resolved_at.isoformat() if p.resolved_at else None,
                )
                for p in proposals
            ]
            conn.executemany(
                """
                INSERT INTO proposals (
                    id, inspection_id, capture_view, bbox_x, bbox_y, bbox_w, bbox_h,
                    checkout_crop_path, checkin_crop_path, checkout_crop_url, checkin_crop_url,
                    condition_type, severity, confidence, description, model_rationale,
                    operator_decision, operator_notes, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.execute(
                "UPDATE inspections SET status = ?, updated_at = ? WHERE id = ?",
                (InspectionStatusEnum.REVIEW_READY.value, now.isoformat(), inspection_id),
            )
        return self.get_inspection(inspection_id)

    def approve_inspection(self, inspection_id: str) -> Inspection:
        """
        Validates all server-side approval preconditions:
        1. All proposals must have decisions (zero 'pending' proposals).
        2. All kit items must have explicit return states (non-null 'is_present_checkin').
        Transitions status to APPROVED if valid, otherwise raises ValueError.
        """
        inspection = self.get_inspection(inspection_id)
        if not inspection:
            raise ValueError(f"Inspection '{inspection_id}' not found.")

        pending_proposals = [
            p.id for p in inspection.proposals if p.operator_decision == ProposalDecisionEnum.PENDING
        ]
        if pending_proposals:
            raise ValueError(
                f"Cannot approve inspection: {len(pending_proposals)} proposals remain unresolved ({', '.join(pending_proposals)})."
            )

        unverified_items = [
            item.name for item in inspection.kit_checklist if item.is_present_checkin is None
        ]
        if unverified_items:
            raise ValueError(
                f"Cannot approve inspection: {len(unverified_items)} kit items unverified ({', '.join(unverified_items)})."
            )

        now = datetime.now(timezone.utc)
        inspection.status = InspectionStatusEnum.APPROVED
        inspection.updated_at = now
        return self.update_inspection(inspection)


# Singleton repository instance
repo = Repository()
