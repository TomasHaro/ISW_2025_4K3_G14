"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Clock, Users, AlertCircle, CheckCircle2, Leaf } from "lucide-react"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api"

type ApiActivity = {
  id: number
  nombre: string
  requiere_talle: boolean
  descripcion?: string
  terms?: string
}

type ApiSlot = {
  id: number
  hora: string
  cupos: number
}

interface Participant {
  name: string
  dni: string
  age: string
  clothingSize?: string
}

export function ActivityRegistration() {
  const [step, setStep] = useState(1)
  const [activities, setActivities] = useState<ApiActivity[]>([])
  const [slotsByActivity, setSlotsByActivity] = useState<Record<string, ApiSlot[]>>({})
  const [loadingActivities, setLoadingActivities] = useState(false)
  const [loadingSlots, setLoadingSlots] = useState<Record<string, boolean>>({})
  const [selectedActivity, setSelectedActivity] = useState<string>("")
  const [selectedTime, setSelectedTime] = useState<string>("")
  const [participantCount, setParticipantCount] = useState<string>("1")
  const [participants, setParticipants] = useState<Participant[]>([{ name: "", dni: "", age: "", clothingSize: "" }])
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

   
  useEffect(() => {
    const handlePopState = () => {
      setStep((prev) => Math.max(1, prev - 1))
    }

    window.addEventListener("popstate", handlePopState)
    return () => window.removeEventListener("popstate", handlePopState)
  }, [])

  useEffect(() => {
    if (step > 1) {
      window.history.pushState({ step }, "", `#step${step}`)
    }
  }, [step])


  // fetch activities on mount
  useEffect(() => {
    async function fetchActivities() {
      setLoadingActivities(true)
      setError(null)
      try {
        const res = await fetch(`${API_BASE}/actividades`)
        if (!res.ok) throw new Error(`Error ${res.status}`)
        const data: ApiActivity[] = await res.json()
        setActivities(data)

        // optional: fetch slots for each activity in parallel to show availability on step 1
        const slotsPromises = data.map(async (a) => {
          try {
            const r = await fetch(`${API_BASE}/actividades/${a.id}/horarios`)
            if (!r.ok) return { id: a.id, slots: [] as ApiSlot[] }
            const s: ApiSlot[] = await r.json()
            return { id: a.id, slots: s }
          } catch {
            return { id: a.id, slots: [] as ApiSlot[] }
          }
        })

        const slotsResults = await Promise.all(slotsPromises)
        const map: Record<string, ApiSlot[]> = {}
        slotsResults.forEach((sr) => {
          map[String(sr.id)] = sr.slots
        })
        setSlotsByActivity(map)
      } catch (e: any) {
        console.error(e)
        setError("No se pudieron cargar las actividades. Reintentá más tarde.")
      } finally {
        setLoadingActivities(false)
      }
    }
    fetchActivities()
  }, [])

  // helper to shape data the UI expects
  const uiActivities = activities.map((a) => {
    const slots = slotsByActivity[String(a.id)] || []
    return {
      id: String(a.id),
      name: a.nombre,
      description: a.descripcion || "Descripción no disponible",
      requiresClothingSize: a.requiere_talle,
      availableSlots: slots.map((s) => ({ time: s.hora, available: s.cupos, slotId: s.id })),
      terms: a.terms || a.descripcion || "No hay condiciones publicadas.",
    }
  })

  const currentActivity = uiActivities.find((a) => a.id === selectedActivity)
  const selectedSlot = currentActivity?.availableSlots.find((s) => s.time === selectedTime)

  const clamp = (value: number, min: number, max: number) => {
  return Math.max(min, Math.min(max, max >= min ? value : min))}


  // select activity and fetch slots if not already loaded
  const handleActivitySelect = async (activityId: string) => {
    setSelectedActivity(activityId)
    setSelectedTime("")
    setStep(2)
    setError(null)

    if (!slotsByActivity[activityId]) {
      setLoadingSlots((prev) => ({ ...prev, [activityId]: true }))
      try {
        const res = await fetch(`${API_BASE}/actividades/${activityId}/horarios`)
        if (!res.ok) throw new Error(`Error ${res.status}`)
        const data: ApiSlot[] = await res.json()
        setSlotsByActivity((prev) => ({ ...prev, [activityId]: data }))
      } catch (e) {
        console.error(e)
        setError("No se pudieron cargar los horarios para la actividad seleccionada.")
      } finally {
        setLoadingSlots((prev) => ({ ...prev, [activityId]: false }))
      }
    }
  }

  const handleTimeSelect = (time: string) => {
    setSelectedTime(time)

    const slot = currentActivity?.availableSlots.find((s) => s.time === time)
    const maxAvailable = slot?.available ?? 1
    const currentCount = Number(participantCount) || 1

    if (currentCount > maxAvailable) {
      setParticipantCount(String(maxAvailable))
      setError(null) 
    }
  }

  const handleParticipantCountChange = (count: string) => {
    const digits = count.replace(/\D/g, "")
    if (digits === "") {
      setParticipantCount("") 
      return
    }

    let numCount = Number(digits) || 1

    const maxAvailable = selectedSlot?.available ?? (currentActivity ? currentActivity.availableSlots.reduce((sum: number, s: any) => Math.max(sum, s.available || 0), 1) : 1)
    numCount = clamp(numCount, 1, maxAvailable)

    setParticipantCount(String(numCount))

    const newParticipants = Array.from(
      { length: numCount },
      (_, i) => participants[i] || { name: "", dni: "", age: "", clothingSize: "" },
    )
    setParticipants(newParticipants)
  }

  const updateParticipant = (index: number, field: keyof Participant, value: string) => {
    const newParticipants = [...participants]
    newParticipants[index] = { ...newParticipants[index], [field]: value }
    setParticipants(newParticipants)
  }

  const canProceedToStep3 = !!selectedActivity && !!selectedTime && !!selectedSlot && selectedSlot.available > 0

  const canSubmit = () => {
    if (!termsAccepted) return false
    if (!currentActivity) return false

    return participants.every((p) => {
      const basicFieldsFilled = Boolean(p.name && p.dni && p.age)
      if (!currentActivity?.requiresClothingSize) return basicFieldsFilled
      return basicFieldsFilled && Boolean(p.clothingSize)
    })
  }

  const handleSubmit = async () => {
    if (!canSubmit() || !currentActivity) return
    setSubmitting(true)
    setError(null)

    const dnis = participants.map((p) => p.dni.trim());
    const uniqueDnis = new Set(dnis);

    if (dnis.length !== uniqueDnis.size) {
      setError("No puede haber dos participantes con el mismo DNI.");
      setSubmitting(false);
      return;
      }

    const payload = {
      nombre_actividad: currentActivity.name,
      horario: selectedTime,
      participantes: participants.map((p) => ({
        nombre: p.name,
        dni: p.dni,
        edad: Number(p.age),
        talle: p.clothingSize || null,
      })),
      aceptar_terminos: true,
    }

    try {
      const res = await fetch(`${API_BASE}/inscripciones`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => null)
        throw new Error(err?.detail || err?.mensaje || `Error ${res.status}`)
      }

      await res.json()
      setSubmitted(true)

      // refresh slots for the selected activity to reflect updated cupos
      if (selectedActivity) {
        try {
          const r2 = await fetch(`${API_BASE}/actividades/${selectedActivity}/horarios`)
          if (r2.ok) {
            const updatedSlots: ApiSlot[] = await r2.json()
            setSlotsByActivity((prev) => ({ ...prev, [selectedActivity]: updatedSlots }))
          }
        } catch (e) {
          // non-blocking: ignore refresh error but log it
          console.error("Error refreshing slots:", e)
        }
      }
    } catch (e: any) {
      console.error(e)
      setError(e.message || "Error al realizar la inscripción.")
    } finally {
      setSubmitting(false)
    }
  }

  const resetForm = () => {
    setStep(1)
    setSelectedActivity("")
    setSelectedTime("")
    setParticipantCount("1")
    setParticipants([{ name: "", dni: "", age: "", clothingSize: "" }])
    setTermsAccepted(false)
    setSubmitted(false)
    setError(null)
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary/5 via-accent/5 to-secondary/10">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
              <CheckCircle2 className="w-10 h-10 text-primary" />
            </div>
            <CardTitle className="text-2xl">¡Inscripción Exitosa!</CardTitle>
            <CardDescription className="text-base">
              Tu reserva para {currentActivity?.name} a las {selectedTime} ha sido confirmada
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted/50 p-4 rounded-lg space-y-2">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Actividad:</strong> {currentActivity?.name}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Horario:</strong> {selectedTime}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Participantes:</strong> {participants.length}
              </p>
            </div>
            <Button onClick={resetForm} className="w-full">
              Realizar otra inscripción
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-accent/5 to-secondary/10 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <Leaf className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold text-foreground">EcoHarmony Park</h1>
          </div>
          <p className="text-lg text-muted-foreground">Inscripción a Actividades</p>
        </div>

        {/* show global errors / loading */}
        {loadingActivities && <p className="text-center">Cargando actividades...</p>}
        {error && (
          <div className="mb-4 p-3 bg-accent/10 border border-accent rounded">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors ${step >= s ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                    }`}
                >
                  {s}
                </div>
                {s < 3 && <div className={`w-12 h-1 mx-2 transition-colors ${step > s ? "bg-primary" : "bg-muted"}`} />}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-sm text-muted-foreground max-w-md mx-auto">
            <span>Actividad</span>
            <span>Horario</span>
            <span>Participantes</span>
          </div>
        </div>

        {/* Step 1: Select Activity */}
        {step === 1 && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Selecciona una Actividad</CardTitle>
                <CardDescription>Elige la actividad que deseas realizar durante tu visita</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {uiActivities.map((activity) => {
                    const hasAvailability = activity.availableSlots.some((s: any) => s.available > 0)
                    return (
                      <Card
                        key={activity.id}
                        className={`cursor-pointer transition-all hover:shadow-md ${selectedActivity === activity.id ? "ring-2 ring-primary" : "hover:border-primary/50"
                          } ${!hasAvailability ? "opacity-60" : ""}`}
                        onClick={() => hasAvailability && handleActivitySelect(activity.id)}
                      >
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <CardTitle className="text-lg">{activity.name}</CardTitle>
                            {!hasAvailability && (
                              <Badge variant="destructive" className="text-xs">
                                Sin cupos
                              </Badge>
                            )}
                          </div>
                          <CardDescription className="text-sm">{activity.description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              <span>1 hora</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              <span>
                                {activity.availableSlots.reduce((sum: number, s: any) => sum + (s.available || 0), 0)} cupos
                              </span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 2: Select Time and Participant Count */}
        {step === 2 && currentActivity && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{currentActivity.name}</CardTitle>
                    <CardDescription>{currentActivity.description}</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setStep(1)}>
                    Cambiar
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Time Selection */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Selecciona el Horario</Label>
                  <RadioGroup value={selectedTime} onValueChange={handleTimeSelect}>
                    <div className="grid gap-3 md:grid-cols-2">
                      {currentActivity.availableSlots.map((slot: any) => (
                        <div key={slot.time} className="relative">
                          <RadioGroupItem
                            value={slot.time}
                            id={slot.time}
                            disabled={slot.available === 0}
                            className="peer sr-only"
                          />
                          <Label
                            htmlFor={slot.time}
                            className={`flex items-center justify-between p-4 rounded-lg border-2 cursor-pointer transition-all ${slot.available === 0 ? "opacity-50 cursor-not-allowed bg-muted" : "hover:border-primary/50 peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5"
                              }`}
                          >
                            <div className="flex items-center gap-3">
                              <Clock className="w-5 h-5 text-muted-foreground" />
                              <span className="font-semibold">{slot.time}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              {slot.available > 0 ? (
                                <>
                                  <Users className="w-4 h-4 text-muted-foreground" />
                                  <span className="text-sm text-muted-foreground">{slot.available} disponibles</span>
                                </>
                              ) : (
                                <Badge variant="destructive" className="text-xs">
                                  Completo
                                </Badge>
                              )}
                            </div>
                          </Label>
                        </div>
                      ))}
                    </div>
                  </RadioGroup>
                </div>

                <Separator />

                {/* Participant Count */}
                <div className="space-y-3">
                  <Label htmlFor="participant-count" className="text-base font-semibold">
                    Cantidad de Participantes
                  </Label>
                  {selectedSlot && (
                    <p className="text-sm text-muted-foreground">Cupos disponibles para este horario: {selectedSlot.available}</p>
                  )}
                  <Input
                    id="participant-count"
                    type="number"
                    inputMode="numeric"
                    min={1}
                    max={selectedSlot?.available ?? 1}
                    value={participantCount}
                    onChange={(e) => handleParticipantCountChange(e.target.value)}
                    className="max-w-xs"
                  />
                </div>

                <div className="flex justify-end">
                  <Button onClick={() => setStep(3)} disabled={!canProceedToStep3} size="lg" >
                    Continuar
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 3: Participant Details and Terms */}
        {step === 3 && currentActivity && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Datos de los Participantes</CardTitle>
                    <CardDescription>Completa la información de cada persona que participará</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setStep(2)}>
                    Volver
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {participants.map((participant, index) => (
                  <div key={index} className="space-y-4 p-4 border rounded-lg bg-card">
                    <h3 className="font-semibold text-lg">Participante {index + 1}</h3>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-2">
                        <Label htmlFor={`name-${index}`}>
                          Nombre Completo <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id={`name-${index}`}
                          type="text"
                          value={participant.name}
                          onChange={(e) => {
                            const value = e.target.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "")
                            updateParticipant(index, "name", value)
                          }}
                          placeholder="Juan Pérez"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`dni-${index}`}>
                          DNI <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id={`dni-${index}`}
                          type="text"               
                          inputMode="numeric"       
                          pattern="\d*"             
                          maxLength={9}             
                          value={participant.dni}
                          onChange={(e) => {
                            // dejar sólo dígitos y cortar a 9
                            const digits = e.target.value.replace(/\D/g, "").slice(0, 9)
                            updateParticipant(index, "dni", digits)
                          }}
                          placeholder="123456789"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`age-${index}`}>
                          Edad <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id={`age-${index}`}
                          type="number"
                          inputMode="numeric"
                          min={0}
                          max={130}
                          value={participant.age}
                          onChange={(e) => {
                            let value = e.target.value.replace(/\D/g, ""); 
                            let num = Number(value);

                            if (num > 130) num = 130; 
                            if (num < 0) num = 0;     

                            updateParticipant(index, "age", num.toString());
                          }}
                          placeholder="25"
                        />
                      </div>
                      {currentActivity.requiresClothingSize && (
                        <div className="space-y-2">
                          <Label htmlFor={`size-${index}`}>
                            Talla de Vestimenta <span className="text-destructive">*</span>
                          </Label>
                          <Select
                            value={participant.clothingSize}
                            onValueChange={(value) => updateParticipant(index, "clothingSize", value)}
                          >
                            <SelectTrigger id={`size-${index}`}>
                              <SelectValue placeholder="Seleccionar talla" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="xs">XS</SelectItem>
                              <SelectItem value="s">S</SelectItem>
                              <SelectItem value="m">M</SelectItem>
                              <SelectItem value="l">L</SelectItem>
                              <SelectItem value="xl">XL</SelectItem>
                              <SelectItem value="xxl">XXL</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                <Separator />

                {/* Terms and Conditions */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Términos y Condiciones</h3>
                  <div className="p-4 bg-muted/50 rounded-lg border">
                    <p className="text-sm text-foreground leading-relaxed">{currentActivity.terms}</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <Checkbox
                      id="terms"
                      checked={termsAccepted}
                      onCheckedChange={(checked) => setTermsAccepted(checked as boolean)}
                    />
                    <Label htmlFor="terms" className="text-sm font-normal leading-relaxed cursor-pointer">
                      Acepto los términos y condiciones específicos de la actividad <span className="text-destructive">*</span>
                    </Label>
                  </div>
                </div>

                {!canSubmit() && (
                  <div className="flex items-start gap-2 p-3 bg-accent/10 border border-accent rounded-lg">
                    <AlertCircle className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                    <p className="text-sm text-foreground">
                      Por favor completa todos los campos requeridos y acepta los términos y condiciones para continuar.
                    </p>
                  </div>
                )}

                <div className="flex justify-end">
                  <Button onClick={handleSubmit} disabled={!canSubmit() || submitting} size="lg" className="min-w-[200px]">
                    {submitting ? "Enviando..." : "Confirmar Inscripción"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
