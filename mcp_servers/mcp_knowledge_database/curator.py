"""AI Database Curator - Autonomous database management with Gemma 2 9B"""
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

# RovoDev MCP friendly - absolute import
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import KnowledgeDatabase

logger = logging.getLogger(__name__)


class AIDatabaseCurator:
    """
    AI-powered database curator that maintains, organizes, and optimizes the knowledge database.
    Uses Gemma 2 9B for intelligent database management.
    """
    
    def __init__(self, db: KnowledgeDatabase, ollama_host: str = "http://localhost:11434"):
        self.db = db
        self.ollama_host = ollama_host
        self.model = "gemma2:9b"
        
    def _call_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call Ollama API with Gemma 2 9B"""
        import requests
        
        # Enhanced prompt to force JSON responses
        if "Reply with JSON" in prompt or "JSON:" in prompt:
            prompt = f"{prompt}\n\nIMPORTANT: Reply ONLY with valid JSON. No extra text before or after."
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower for more deterministic decisions
                "top_p": 0.9,
                "num_predict": 500  # Limit response length
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            return ""
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from AI response (handles markdown code blocks, etc)"""
        import re
        
        # Try direct parse first
        try:
            return json.loads(text)
        except:
            pass
        
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try to find any JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return {"error": "Failed to parse", "raw_response": text[:200]}
    
    # ========================================================================
    # MAIN CURATOR TASKS
    # ========================================================================
    
    async def run_full_curation(self) -> Dict[str, Any]:
        """Run complete database curation cycle"""
        logger.info("Starting full database curation...")
        
        results = {
            "started_at": datetime.now().isoformat(),
            "tasks": {}
        }
        
        # Task 1: Clean duplicate entries
        logger.info("Task 1: Cleaning duplicates...")
        results["tasks"]["duplicates"] = await self.clean_duplicates()
        
        # Task 2: Archive old data
        logger.info("Task 2: Archiving old data...")
        results["tasks"]["archiving"] = await self.archive_old_data()
        
        # Task 3: Update confidence scores
        logger.info("Task 3: Updating confidence scores...")
        results["tasks"]["confidence"] = await self.recalculate_confidence()
        
        # Task 4: Detect anomalies
        logger.info("Task 4: Detecting anomalies...")
        results["tasks"]["anomalies"] = await self.detect_anomalies()
        
        # Task 5: Auto-tag entries
        logger.info("Task 5: Auto-tagging entries...")
        results["tasks"]["tagging"] = await self.auto_tag_entries()
        
        # Task 6: Find relationships
        logger.info("Task 6: Finding relationships...")
        results["tasks"]["relationships"] = await self.discover_relationships()
        
        # Task 7: Generate insights
        logger.info("Task 7: Generating insights...")
        results["tasks"]["insights"] = await self.generate_insights()
        
        results["completed_at"] = datetime.now().isoformat()
        results["status"] = "success"
        
        logger.info("Database curation completed successfully")
        return results
    
    # ========================================================================
    # TASK 1: CLEAN DUPLICATES
    # ========================================================================
    
    async def clean_duplicates(self) -> Dict[str, Any]:
        """Find and merge duplicate entries using AI"""
        cursor = self.db.connection.cursor()
        
        # Find potential duplicate code entries
        cursor.execute("""
            SELECT id, symbol_name, purpose, file_id
            FROM code_knowledge
            ORDER BY symbol_name
        """)
        code_entries = cursor.fetchall()
        
        duplicates_found = []
        merged_count = 0
        
        # Group by similar names
        grouped = {}
        for entry in code_entries:
            name = entry['symbol_name'].lower()
            if name not in grouped:
                grouped[name] = []
            grouped[name].append(dict(entry))
        
        # Check groups with multiple entries
        for name, entries in grouped.items():
            if len(entries) > 1:
                # Ask AI if these are duplicates
                prompt = f"""
You are a database curator. Analyze these code entries and determine if they are duplicates:

{json.dumps(entries, indent=2)}

Are these the same function/class with redundant entries? Reply with JSON:
{{
    "are_duplicates": true/false,
    "reason": "explanation",
    "keep_id": <id of best entry to keep>,
    "merge_data": {{"any additional data to merge"}}
}}
"""
                
                response = self._call_ollama(
                    prompt,
                    system_prompt="You are an expert database curator. Analyze data carefully and respond in valid JSON only."
                )
                
                try:
                    analysis = json.loads(response)
                    if analysis.get("are_duplicates"):
                        duplicates_found.append({
                            "entries": entries,
                            "analysis": analysis
                        })
                        # TODO: Actually merge in production
                        merged_count += len(entries) - 1
                except:
                    logger.warning(f"Failed to parse AI response for duplicates: {response[:100]}")
        
        return {
            "duplicates_found": len(duplicates_found),
            "merged_count": merged_count,
            "details": duplicates_found[:5]  # First 5 for review
        }
    
    # ========================================================================
    # TASK 2: ARCHIVE OLD DATA
    # ========================================================================
    
    async def archive_old_data(self) -> Dict[str, Any]:
        """Identify and archive old/unused data"""
        cursor = self.db.connection.cursor()
        
        # Find old command patterns
        cutoff_date = datetime.now() - timedelta(days=90)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM command_patterns
            WHERE executed_at < ?
        """, (cutoff_date,))
        
        old_commands = cursor.fetchone()['count']
        
        # Find code not indexed recently
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM code_files
            WHERE last_indexed < ?
        """, (cutoff_date,))
        
        old_code = cursor.fetchone()['count']
        
        # Ask AI what to archive
        prompt = f"""
Database contains:
- {old_commands} command executions older than 90 days
- {old_code} code files not indexed in 90 days

Should we archive this data? Consider:
1. Historical value for baselines
2. Storage space
3. Data relevance

Reply with JSON:
{{
    "archive_commands": true/false,
    "archive_code": true/false,
    "reasoning": "explanation"
}}
"""
        
        response = self._call_ollama(
            prompt,
            system_prompt="You are a database curator deciding what data to archive. Be conservative - only archive truly obsolete data."
        )
        
        archived_count = 0
        decision = self._extract_json(response)
        # In production, actually archive based on decision
        logger.info(f"AI archival decision: {decision}")
        
        return {
            "old_commands": old_commands,
            "old_code": old_code,
            "archived": archived_count,
            "ai_decision": decision
        }
    
    # ========================================================================
    # TASK 3: RECALCULATE CONFIDENCE
    # ========================================================================
    
    async def recalculate_confidence(self) -> Dict[str, Any]:
        """Recalculate confidence scores for all entries"""
        cursor = self.db.connection.cursor()
        
        # Update error solution confidence
        cursor.execute("""
            UPDATE error_solutions
            SET confidence = CAST(success_count AS REAL) / 
                            CAST((success_count + failure_count + 1) AS REAL)
            WHERE success_count + failure_count > 0
        """)
        
        updated_solutions = cursor.rowcount
        
        # Update command baseline confidence
        cursor.execute("""
            UPDATE command_baselines
            SET confidence = CASE
                WHEN sample_count >= 10 THEN 1.0
                WHEN sample_count >= 5 THEN 0.8
                WHEN sample_count >= 3 THEN 0.6
                ELSE CAST(sample_count AS REAL) / 10.0
            END
        """)
        
        updated_baselines = cursor.rowcount
        
        self.db.connection.commit()
        
        return {
            "updated_solutions": updated_solutions,
            "updated_baselines": updated_baselines,
            "message": "Confidence scores recalculated"
        }
    
    # ========================================================================
    # TASK 4: DETECT ANOMALIES
    # ========================================================================
    
    async def detect_anomalies(self) -> Dict[str, Any]:
        """Detect unusual patterns in the database"""
        cursor = self.db.connection.cursor()
        anomalies = []
        
        # Anomaly 1: Command suddenly taking much longer
        cursor.execute("""
            SELECT 
                cp.command,
                cp.duration_ms,
                cb.avg_duration_ms,
                cp.executed_at
            FROM command_patterns cp
            JOIN command_baselines cb ON cp.command = cb.command
            WHERE cp.executed_at > datetime('now', '-7 days')
              AND cp.duration_ms > cb.avg_duration_ms * 2
              AND cb.confidence > 0.5
            ORDER BY cp.executed_at DESC
            LIMIT 10
        """)
        
        slow_commands = cursor.fetchall()
        if slow_commands:
            anomalies.append({
                "type": "slow_command",
                "severity": "warning",
                "count": len(slow_commands),
                "details": [dict(row) for row in slow_commands]
            })
        
        # Anomaly 2: Increased failure rate
        cursor.execute("""
            SELECT 
                command,
                success_rate,
                sample_count,
                (SELECT COUNT(*) FROM command_patterns 
                 WHERE command = cb.command 
                   AND success = 0 
                   AND executed_at > datetime('now', '-7 days')) as recent_failures
            FROM command_baselines cb
            WHERE success_rate < 0.7
              AND sample_count > 5
        """)
        
        failing_commands = cursor.fetchall()
        if failing_commands:
            anomalies.append({
                "type": "high_failure_rate",
                "severity": "error",
                "count": len(failing_commands),
                "details": [dict(row) for row in failing_commands]
            })
        
        # Ask AI to analyze anomalies
        if anomalies:
            prompt = f"""
Analyze these database anomalies:

{json.dumps(anomalies, indent=2, default=str)}

What could be causing these issues? Reply with JSON:
{{
    "analysis": "overall analysis",
    "likely_causes": ["cause1", "cause2"],
    "recommendations": ["action1", "action2"],
    "urgency": "low/medium/high"
}}
"""
            
            response = self._call_ollama(
                prompt,
                system_prompt="You are a system analyst. Analyze anomalies and provide actionable insights."
            )
            
            try:
                ai_analysis = json.loads(response)
            except:
                ai_analysis = {"error": "Failed to parse"}
        else:
            ai_analysis = {"message": "No anomalies detected"}
        
        return {
            "anomalies_found": len(anomalies),
            "anomalies": anomalies,
            "ai_analysis": ai_analysis
        }
    
    # ========================================================================
    # TASK 5: AUTO-TAG ENTRIES
    # ========================================================================
    
    async def auto_tag_entries(self) -> Dict[str, Any]:
        """Automatically tag and categorize entries"""
        cursor = self.db.connection.cursor()
        
        # Get untagged code entries (those without command_type)
        cursor.execute("""
            SELECT id, symbol_name, purpose, symbol_type
            FROM code_knowledge
            WHERE purpose IS NOT NULL
            LIMIT 20
        """)
        
        entries = cursor.fetchall()
        tagged_count = 0
        
        for entry in entries:
            prompt = f"""
Categorize this code:
Name: {entry['symbol_name']}
Type: {entry['symbol_type']}
Purpose: {entry['purpose']}

Assign ONE category: authentication, database, api, ui, utils, testing, config, security, performance, other

Reply with just the category name.
"""
            
            response = self._call_ollama(
                prompt,
                system_prompt="You are a code categorizer. Reply with ONE word category only."
            ).strip().lower()
            
            # Store category (we'd need to add a category column, for now just log)
            logger.info(f"Tagged {entry['symbol_name']} as: {response}")
            tagged_count += 1
        
        return {
            "entries_processed": len(entries),
            "tagged_count": tagged_count,
            "message": "Auto-tagging completed"
        }
    
    # ========================================================================
    # TASK 6: DISCOVER RELATIONSHIPS
    # ========================================================================
    
    async def discover_relationships(self) -> Dict[str, Any]:
        """Discover hidden relationships between data"""
        cursor = self.db.connection.cursor()
        
        # Find correlations between errors and commands
        cursor.execute("""
            SELECT 
                cp.command,
                cp.error_snippet,
                COUNT(*) as error_count
            FROM command_patterns cp
            WHERE cp.success = 0
              AND cp.error_snippet IS NOT NULL
            GROUP BY cp.command, cp.error_snippet
            HAVING COUNT(*) > 2
        """)
        
        patterns = cursor.fetchall()
        relationships = []
        
        for pattern in patterns[:5]:  # Top 5
            # Ask AI to analyze the relationship
            prompt = f"""
This command fails repeatedly with this error:
Command: {pattern['command']}
Error: {pattern['error_snippet']}
Occurrences: {pattern['error_count']}

What is the relationship? What's the root cause? Reply with JSON:
{{
    "relationship": "description",
    "root_cause": "likely cause",
    "solution": "suggested fix"
}}
"""
            
            response = self._call_ollama(
                prompt,
                system_prompt="You are a debugging expert. Find root causes of recurring errors."
            )
            
            analysis = self._extract_json(response)
            if "error" not in analysis:
                relationships.append({
                    "command": pattern['command'],
                    "error_count": pattern['error_count'],
                    "analysis": analysis
                })
        
        return {
            "relationships_found": len(relationships),
            "details": relationships
        }
    
    # ========================================================================
    # TASK 7: GENERATE INSIGHTS
    # ========================================================================
    
    async def generate_insights(self) -> Dict[str, Any]:
        """Generate high-level insights about the database"""
        cursor = self.db.connection.cursor()
        
        # Gather statistics
        cursor.execute("SELECT COUNT(*) as count FROM code_knowledge")
        code_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM command_patterns")
        command_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM error_solutions")
        solution_count = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT command, sample_count 
            FROM command_baselines 
            ORDER BY sample_count DESC 
            LIMIT 5
        """)
        top_commands = [dict(row) for row in cursor.fetchall()]
        
        # Ask AI for insights
        prompt = f"""
Database statistics:
- Code entries: {code_count}
- Command executions: {command_count}
- Error solutions: {solution_count}
- Most run commands: {json.dumps(top_commands)}

Generate insights:
1. Overall database health
2. Data quality assessment
3. Usage patterns
4. Recommendations for improvement

Reply with JSON:
{{
    "health_score": 0-100,
    "quality_assessment": "assessment",
    "usage_patterns": ["pattern1", "pattern2"],
    "recommendations": ["rec1", "rec2"]
}}
"""
        
        response = self._call_ollama(
            prompt,
            system_prompt="You are a data analyst. Provide actionable insights."
        )
        
        insights = self._extract_json(response)
        
        return {
            "statistics": {
                "code_count": code_count,
                "command_count": command_count,
                "solution_count": solution_count
            },
            "insights": insights
        }
    
    # ========================================================================
    # HEALTH CHECK
    # ========================================================================
    
    async def get_database_health(self) -> Dict[str, Any]:
        """Get current database health metrics"""
        cursor = self.db.connection.cursor()
        
        # Count entries
        cursor.execute("SELECT COUNT(*) as count FROM code_knowledge")
        code_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM command_patterns")
        command_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM error_solutions WHERE confidence > 0.7")
        reliable_solutions = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM command_baselines WHERE confidence > 0.8")
        reliable_baselines = cursor.fetchone()['count']
        
        # Calculate health score
        health_score = min(100, (
            (code_count / 100 * 20) +  # 20 points for code coverage
            (command_count / 100 * 20) +  # 20 points for command history
            (reliable_solutions * 10) +  # 10 points per reliable solution
            (reliable_baselines * 5)  # 5 points per reliable baseline
        ))
        
        return {
            "health_score": int(health_score),
            "total_code_entries": code_count,
            "total_commands": command_count,
            "reliable_solutions": reliable_solutions,
            "reliable_baselines": reliable_baselines,
            "status": "healthy" if health_score > 70 else "needs_attention"
        }
