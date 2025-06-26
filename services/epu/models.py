from sqlalchemy import Column, Integer, String, Sequence, func, text
from common.database import Base, db_session
from datetime import datetime


class Epu(Base):
    __tablename__ = 'SFEPUS_MAE_NUC_CAB' # Oracle usa convención de mayúsculas
    __table_args__ = {'schema': 'ROOT'}
    # Usar Sequence para autoincrementales en Oracle
    id = Column('ID', Integer, Sequence('epu_id_seq'), primary_key=True)
    alta = Column('ALTA', String(4), nullable=False)
    cuenta = Column('CUENTA', String(50), unique=True, nullable=False)
    vcto_ano = Column('VCTO_ANO', String(4), nullable=False)
    vcto_mes = Column('VCTO_MES', String(2), nullable=False)
    vcto = Column('VCTO', String(20), nullable=False)

    def to_dict(self):
        return {
            'ID': self.id,
            'ALTA': self.alta,
            'CUENTA': self.cuenta,
            'VCTO_ANO': self.vcto_ano,
            'VCTO_MES': self.vcto_mes,
            'VCTO': self.vcto
        }

    @classmethod
    def obtener_facturacion(cls, cuenta, dateInit, dateEnd):
        session = db_session()
        try:
            if isinstance(dateInit, str):
                dateInit = datetime.strptime(dateInit, "%Y-%m-%d").date()
            if isinstance(dateEnd, str):
                dateEnd = datetime.strptime(dateEnd, "%Y-%m-%d").date()

            fecha_vcto = func.to_date(
                func.concat(cls.vcto_ano, func.concat('-', func.concat(cls.vcto_mes, '-01'))),
                'YYYY-MM-DD'
            )
            result = session.query(cls).filter(
                cls.cuenta == cuenta,
                fecha_vcto >= dateInit,
                fecha_vcto <= dateEnd
            ).all()

            return [r.to_dict() for r in result]
        except Exception as e:
          print(f"Error en obtener_facturacion: {str(e)}")
          return []
        finally:
            session.close()
    
    @classmethod
    def obtener_facturacion_sp(cls, entidad, cen_alt, cuenta):
        session = db_session()
        connection = session.connection().connection  # Objeto cx_Oracle
        try:
            import cx_Oracle
            cursor = connection.cursor()
            # Prepara los parámetros de salida
            out_cursor = connection.cursor()
            snum_status = cursor.var(cx_Oracle.NUMBER)
            svc2_mensj = cursor.var(cx_Oracle.STRING)
            # Llama al procedimiento
            cursor.callproc(
                "SFEPUS_PRC_COS_FCH_FCN",
                [entidad, cen_alt, cuenta, out_cursor, snum_status, svc2_mensj]
            )
            # Obtiene los resultados del cursor de salida
            resultados = []
            for row in out_cursor:
                resultados.append({
                    "fch_fcn": row[0],
                    "fch_vnc": row[1]
                })
            out_cursor.close()
            cursor.close()
            return {
                "status": int(snum_status.getvalue()),
                "mensaje": svc2_mensj.getvalue(),
                "data": resultados
            }
        except Exception as e:
            print(f"Error llamando al procedimiento: {str(e)}")
            return {
                "status": -1,
                "mensaje": str(e),
                "data": []
            }
        finally:
            session.close()